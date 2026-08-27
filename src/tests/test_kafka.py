import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from aloha.testing.unit import UnitTestCase
from aloha.db.kafka import KafkaOperator, ConsumedMessage, _unpack_message, _prepare_headers
from aloha.db.kafka_aio import KafkaOperator as KafkaOperatorAio, ConsumedMessage as ConsumedMessageAio


class TestKafkaHelpers(UnitTestCase):
    def test_unpack_message(self):
        # 1. string input
        val, key, headers = _unpack_message("hello")
        self.assertEqual(val, "hello")
        self.assertIsNone(key)
        self.assertIsNone(headers)

        # 2. dict input
        val, key, headers = _unpack_message({"value": "hello", "key": "k", "headers": {"h": "v"}})
        self.assertEqual(val, "hello")
        self.assertEqual(key, "k")
        self.assertEqual(headers, {"h": "v"})

        # 3. object/ConsumedMessage input
        msg = ConsumedMessage(topic="t", partition=0, offset=0, key="k", value="hello", headers=[("h", "v")])
        val, key, headers = _unpack_message(msg)
        self.assertEqual(val, "hello")
        self.assertEqual(key, "k")
        self.assertEqual(headers, [("h", "v")])

    def test_prepare_headers(self):
        # dict headers
        hdrs = _prepare_headers({"tenant_id": "123", "trace_id": "abc"})
        self.assertEqual(hdrs, [("tenant_id", b"123"), ("trace_id", b"abc")])

        # list headers with string and bytes values
        hdrs = _prepare_headers([("tenant_id", "123"), ("trace_id", b"abc"), ("empty", None)])
        self.assertEqual(hdrs, [("tenant_id", b"123"), ("trace_id", b"abc"), ("empty", b"")])


class TestSyncKafkaOperator(UnitTestCase):
    @patch("confluent_kafka.Producer")
    def test_producer_singleton_and_deliver(self, mock_producer_cls):
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer

        config = {"host": [{"host": "localhost", "port": 9092}]}
        op = KafkaOperator(config)

        # Producer is lazily created
        p1 = op.producer()
        p2 = op.producer()
        self.assertIs(p1, p2)
        mock_producer_cls.assert_called_once()

        # Test producer_deliver
        generator = ["msg1", {"value": "msg2", "key": "k2", "headers": {"h2": "v2"}}]
        op.producer_deliver("my_topic", generator)

        # Check mock calls
        self.assertEqual(mock_producer.produce.call_count, 2)
        # First call: string only
        mock_producer.produce.assert_any_call(
            "my_topic", value=b"msg1", key=None, headers=None, callback=mock_producer.produce.call_args_list[0][1]["callback"]
        )
        # Second call: dict with key and headers
        mock_producer.produce.assert_any_call(
            "my_topic", value=b"msg2", key="k2", headers=[("h2", b"v2")], callback=mock_producer.produce.call_args_list[1][1]["callback"]
        )
        mock_producer.flush.assert_called_once()

        # Context manager exit calls close() and flushes/cleans up producer
        op.close()
        self.assertIsNone(op._producer)

    @patch("confluent_kafka.Consumer")
    def test_consumer_generator_and_commit(self, mock_consumer_cls):
        mock_consumer = MagicMock()
        mock_consumer_cls.return_value = mock_consumer

        # Mocking poll to return one message, then raise exception to exit
        mock_msg = MagicMock()
        mock_msg.topic.return_value = "my_topic"
        mock_msg.partition.return_value = 0
        mock_msg.offset.return_value = 100
        mock_msg.key.return_value = b"my_key"
        mock_msg.value.return_value = b"my_value"
        mock_msg.headers.return_value = [("h", b"v")]
        mock_msg.error.return_value = None

        mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt("stop")]

        config = {"host": [{"host": "localhost", "port": 9092}]}
        op = KafkaOperator(config)

        gen = op.consumer_generator(["my_topic"], group_id="my_group")
        try:
            msg = next(gen)
            self.assertIsInstance(msg, ConsumedMessage)
            self.assertEqual(msg.topic, "my_topic")
            self.assertEqual(msg.partition, 0)
            self.assertEqual(msg.offset, 100)
            self.assertEqual(msg.key, "my_key")
            self.assertEqual(msg.value, "my_value")
            self.assertEqual(msg.headers, [("h", "v")])

            # Commit calls mock consumer commit
            op.commit()
            mock_consumer.commit.assert_called_once()

            # Continue generator to trigger KeyboardInterrupt/finally block
            next(gen)
        except KeyboardInterrupt:
            pass

        # Ensure consumer is closed and cleared
        mock_consumer.close.assert_called_once()
        self.assertIsNone(op._consumer)


class TestAsyncKafkaOperator(UnitTestCase):
    def test_producer_singleton_and_deliver(self):
        async def run_test():
            with patch("aiokafka.AIOKafkaProducer") as mock_producer_cls:
                mock_producer = MagicMock()
                mock_producer.start = AsyncMock()
                mock_producer.stop = AsyncMock()
                mock_producer.send_and_wait = AsyncMock()
                mock_producer_cls.return_value = mock_producer

                config = {"host": [{"host": "localhost", "port": 9092}]}
                op = KafkaOperatorAio(config)

                # Producer singleton
                p1 = await op.producer()
                p2 = await op.producer()
                self.assertIs(p1, p2)
                mock_producer.start.assert_called_once()

                # Test producer_deliver
                async def mock_generator():
                    yield "msg1"
                    yield {"value": "msg2", "key": "k2", "headers": {"h2": "v2"}}

                mock_callback = AsyncMock()
                await op.producer_deliver("my_topic", mock_generator(), func_callback=mock_callback)

                self.assertEqual(mock_producer.send_and_wait.call_count, 2)
                mock_producer.send_and_wait.assert_any_call(
                    "my_topic", value="msg1", key=None, headers=None
                )
                mock_producer.send_and_wait.assert_any_call(
                    "my_topic", value="msg2", key="k2", headers=[("h2", b"v2")]
                )
                # Check that callback was called
                self.assertEqual(mock_callback.call_count, 2)

                # Close stops producer
                await op.close()
                mock_producer.stop.assert_called_once()
                self.assertIsNone(op._producer)

        asyncio.run(run_test())

    def test_consumer_generator_and_commit(self):
        async def run_test():
            with patch("aiokafka.AIOKafkaConsumer") as mock_consumer_cls:
                mock_consumer = MagicMock()
                mock_consumer.start = AsyncMock()
                mock_consumer.stop = AsyncMock()
                mock_consumer.commit = AsyncMock()

                # Mocking async iterator on consumer
                mock_msg = MagicMock()
                mock_msg.topic = "my_topic"
                mock_msg.partition = 0
                mock_msg.offset = 100
                mock_msg.key = "my_key"
                mock_msg.value = "my_value"
                mock_msg.headers = [("h", b"v")]

                async def mock_aiter(self_iter):
                    yield mock_msg

                mock_consumer.__aiter__ = mock_aiter
                mock_consumer_cls.return_value = mock_consumer

                config = {"host": [{"host": "localhost", "port": 9092}]}
                op = KafkaOperatorAio(config)

                gen = op.consumer_generator(["my_topic"], group_id="my_group")
                async for msg in gen:
                    self.assertIsInstance(msg, ConsumedMessageAio)
                    self.assertEqual(msg.topic, "my_topic")
                    self.assertEqual(msg.partition, 0)
                    self.assertEqual(msg.offset, 100)
                    self.assertEqual(msg.key, "my_key")
                    self.assertEqual(msg.value, "my_value")
                    self.assertEqual(msg.headers, [("h", "v")])

                    # Commit
                    await op.commit()
                    mock_consumer.commit.assert_called_once()

                mock_consumer.stop.assert_called_once()
                self.assertIsNone(op._consumer)

        asyncio.run(run_test())

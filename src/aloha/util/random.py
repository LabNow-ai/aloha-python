__all__ = (
    "random",
    "random_bool",
    "random_choice",
    "random_int",
    "random_ratio",
    "random_uniform",
    "random_sample",
    "random_seed",
)

from secrets import SystemRandom

random = SystemRandom()


def random_bool():
    return random.choice([True, False])


random_choice = random.choice


random_int = random.randint


random_ratio = random.random


random_uniform = random.uniform


random_sample = random.sample


random_seed = random.seed

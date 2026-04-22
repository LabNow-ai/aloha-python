"""Version 1 signed JSON API helpers.

Version 1 adds request signing with `app_id`, `salt_uuid`, and `sign` fields.
Handlers validate the signature before dispatching to the service logic.
"""

__all__ = ("APIHandler", "APICaller", "sign_data", "sign_check")

import json
import logging
import uuid
from abc import ABC

from ...encrypt.hash import get_md5_of_str, get_sha256_of_str
from ...settings import SETTINGS
from ..http import AbstractApiClient, AbstractApiHandler

APP_ID_KEYS = SETTINGS.config.get("APP_ID_KEYS", {})
APP_OPTIONS = SETTINGS.config.get("APP_OPTIONS", {})
FUNC_SIGN_CHECK = {"md5": get_md5_of_str, "sha256": get_sha256_of_str}
func_sign_check_default = FUNC_SIGN_CHECK.get(APP_OPTIONS.get("sign_method", "md5"))


class APIHandler(AbstractApiHandler, ABC):
    """Signed API handler for v1 endpoints."""

    MAP_ERROR_INFO = {
        "BAD_REQUEST": {"code": "5101", "message": ["Bad request: fail to parse body as JSON object!"]},
        "MISSING_ARGS": {"code": "5102", "message": ["Required argument field(s) missing..."]},
        "SIGN_CHECK_FAIL": {"code": "5104", "message": ["Invalid sign, sign check failed!"]},
    }

    async def post(self):
        """Validate the signature and dispatch the wrapped payload."""
        body_arguments = self.request_body

        try:
            salt_uuid = body_arguments.pop("salt_uuid")
            app_id = body_arguments.pop("app_id")
            sign = body_arguments.pop("sign")
            data = body_arguments.pop("data")
        except KeyError:  # cannot find default key from parsed body
            return self.finish(self.MAP_ERROR_INFO["MISSING_ARGS"])

        is_valid_req = sign_check(salt_uuid=salt_uuid, app_id=app_id, sign=sign, data=data)  # , sign_method='sha256'
        if not is_valid_req:
            return self.finish(self.MAP_ERROR_INFO["SIGN_CHECK_FAIL"])

        resp = dict(code=5200, message=["success"])
        try:
            result = self.response(**data)  # this call may throw TypeError when argument missing
            resp["data"] = result
            resp["salt_uuid"] = salt_uuid
        except Exception as e:
            if self.LOG.level == logging.DEBUG:
                self.LOG.error(e, exc_info=True)
            return self.finish({"code": 5201, "message": [repr(e)]})

        resp = json.dumps(resp, ensure_ascii=False, default=str, separators=(",", ":"))
        return self.finish(resp)


class APICaller(AbstractApiClient):
    """Client helper that wraps payloads with v1 signing metadata."""

    APP_ID_KEYS = AbstractApiClient.config.get("APP_ID_KEYS", {})

    def wrap_request_data(
        self,
        data,
        app_id: str | None = None,
        app_key: str | None = None,
        salt_uuid: str | None = None,
        sign: str | None = None,
        sign_method: str | None = None,
    ):
        """Wrap the payload with signature fields expected by v1 handlers."""
        if app_id is None:
            # if len(APP_ID_KEYS) != 1:
            #     raise RuntimeError('Please specify 1 and only 1 in APP_ID_KEYS in configurations!')
            app_id = list(self.APP_ID_KEYS.keys())[0]
        salt_uuid = salt_uuid or str(uuid.uuid1())
        sign = sign or sign_data(
            salt_uuid=salt_uuid,
            app_id=app_id,
            app_key=app_key or self.APP_ID_KEYS.get(app_id),
            data=data,
            sign_method=sign_method,
        )
        return {"salt_uuid": salt_uuid, "app_id": app_id, "sign": sign, "data": data}


def sign_data(salt_uuid: str, app_id: str, app_key: str, data, sign_method: str = None):
    """Generate the v1 signature for a payload.

    The signature is based on `app_id + salt_uuid + data + app_key`.
    """
    data_str = str(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    public_key = app_id + salt_uuid + data_str + app_key

    func_sign_check = func_sign_check_default if sign_method is None else FUNC_SIGN_CHECK.get(sign_method)
    if func_sign_check is None:
        raise ValueError("Invalid `sign_method`: %s" % sign_method)
    sign = func_sign_check(public_key)
    return sign


def sign_check(salt_uuid: str, app_id: str, sign: str, data, sign_method: str = None, date_time=None):
    """Validate a v1 request signature."""

    func_sign_check = func_sign_check_default if sign_method is None else FUNC_SIGN_CHECK.get(sign_method)
    if func_sign_check is None:
        raise ValueError("Invalid `sign_method`: %s" % sign_method)

    app_key = APP_ID_KEYS.get(app_id)
    if app_key is None:  # APP_ID not in the dict, unknown APP_ID
        return False

    # data_str = str(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')))

    # --> Compatible with older version API
    right_sign = func_sign_check(app_id + salt_uuid + app_key)
    if sign == right_sign:
        return True
    # <--

    public_key = str(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    public_key = app_id + salt_uuid + public_key + app_key
    right_sign = func_sign_check(public_key)
    return sign == right_sign

import requests
import logging

logger = logging.getLogger(__name__)

try:
    import json
except ImportError:
    import simplejson as json


class APIException(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message


class HTTPException(Exception):
    pass


class KavenegarAPI(object):
    def __init__(self, apikey):
        self.version = 'v1'
        self.host = 'api.kavenegar.com'
        self.apikey = apikey
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }

    def __repr__(self):
        return "kavenegar.KavenegarAPI({!r})".format(self.apikey)

    def __str__(self):
        return "kavenegar.KavenegarAPI({!s})".format(self.apikey)

    def _request(self, action, method, params={}):
        url = 'https://' + self.host + '/' + self.version + '/' + self.apikey + '/' + action + '/' + method + '.json'
        try:
            content = requests.post(url, headers=self.headers, auth=None, data=params).content
            try:
                response = json.loads(content.decode("utf-8"))
                if (response['return']['status'] == 200):
                    response = response['entries']
                else:
                    e = APIException(response['return']['status'], response['return']['message'])
                    logger.error(e)
                    raise e
            except ValueError as e:
                logger.error(e)
                raise HTTPException(e)
            return (response)
        except requests.exceptions.RequestException as e:
            raise HTTPException(e)

    def sms_send(self, params=None):
        return self._request('sms', 'send', params)

    def sms_sendarray(self, params=None):
        return self._request('sms', 'sendarray', params)

    def sms_status(self, params=None):
        return self._request('sms', 'status', params)

    def sms_statuslocalmessageid(self, params=None):
        return self._request('sms', 'statuslocalmessageid', params)

    def sms_select(self, params=None):
        return self._request('sms', 'select', params)

    def sms_selectoutbox(self, params=None):
        return self._request('sms', 'selectoutbox', params)

    def sms_latestoutbox(self, params=None):
        return self._request('sms', 'latestoutbox', params)

    def sms_countoutbox(self, params=None):
        return self._request('sms', 'countoutbox', params)

    def sms_cancel(self, params=None):
        return self._request('sms', 'cancel', params)

    def sms_receive(self, params=None):
        return self._request('sms', 'receive', params)

    def sms_countinbox(self, params=None):
        return self._request('sms', 'countinbox', params)

    def sms_countpostalcode(self, params=None):
        return self._request('sms', 'countpostalcode', params)

    def sms_sendbypostalcode(self, params=None):
        return self._request('sms', 'sendbypostalcode', params)

    def verify_lookup(self, params=None):
        return self._request('verify', 'lookup', params)

    def call_maketts(self, params=None):
        return self._request('call', 'maketts', params)

    def call_status(self, params=None):
        return self._request('call', 'status', params)

    def account_info(self):
        return self._request('account', 'info')

    def account_config(self, params=None):
        return self._request('account', 'config', params)


class KavenegarMessageStatus:

    OK = 200
    INVALID_PARAMETERS = 400
    ACCOUNT_DISABLED = 401
    OPERATION_FAILED = 402
    INVALID_API_KEY = 403
    INVALID_METHOD = 404
    INVALID_GET_POST = 405
    PARAMETER_IS_EMPTY = 406
    CAN_NOT_ACCESS_DATA = 407
    SERVER_NOT_RESPONDING = 409
    INVALID_RECEPTOR = 411
    INVALID_SENDER = 412
    EMPTY_OR_HUGE_TEXT = 413
    INVALID_REQUEST_NUM = 414
    START_INDEX_BIGGER_THAN_LENGTH = 415
    IP_MISMATCH = 416
    INVALID_SEND_DATE = 417
    NOT_ENOUGH_CREDIT = 418
    RECEPTOR_SENDER_ARRAY_LENGTH_MISMATCH = 419
    CAN_NOT_USE_LINK_IN_TEXT = 420
    INVALID_CHARACTERS_IN_DATA = 422
    PATTERN_NOT_FOUND = 424
    METHOD_NEEDS_ADVANCED_ACCOUNT = 426
    CAN_NOT_SEND_CODE_IN_VOICE_CALL = 428
    IP_LIMITED = 429
    INVALID_CODE_STRUCTURE = 431
    CODE_NOT_FOUND_IN_TEXT = 432


import json
from json import JSONDecodeError

import grpc
from django.conf import settings
from google.protobuf.json_format import MessageToDict
from grpc._channel import _InactiveRpcError

from utils.func_utils import is_json


def decode_data(data):
    if not data:
        return None
    elif isinstance(data, (dict, list)):
        return json.loads(data)

    try:
        data = json.loads(data)
    except JSONDecodeError:
        pass
    return data


def run(stub_class,  # in pb2_grpc file          ps.  obbyauth_pb2_grpc.AuthStub
        request_message,  # in pb2 file          ps.  CreateRequest(account='test')
        func: str,  # in stub                    ps.  stub.TestCreate, AuthStub的TestCreate传入'TestCreate'
        raise_exception=False,
        other_reply=False):
    with grpc.insecure_channel(settings.RPC_HOST) as channel:
        stub = stub_class(channel)
        try:
            reply = stub.__dict__.get(func)(request_message)
        except _InactiveRpcError as e:
            from utils.exceptions import CustomAPIException
            print('Exception raised: ', str(e))
            raise CustomAPIException(500, '服务繁忙，请稍后再试')

    reply_dict = MessageToDict(reply, preserving_proto_field_name=True)
    if reply_dict.get('code') != 200 and raise_exception:
        json_or_not = is_json(reply_dict.get('message'))
        from utils.exceptions import CustomAPIException
        if json_or_not:
            raise CustomAPIException(code=reply_dict.get('code'), message=json_or_not)
        raise CustomAPIException(code=reply_dict.get('code'), message=reply_dict.get('message'))
    elif reply_dict.get('code') != 200 and not raise_exception:
        return reply_dict.get('code'), json.loads(reply_dict.get('message'))

    if other_reply:
        return reply_dict

    return decode_data(reply_dict.get('data'))

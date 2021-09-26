"""自定义视图与接口相关辅助类"""
import re
import traceback

from django.conf import settings
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from django.http import Http404, JsonResponse
from rest_framework import exceptions, status
from rest_framework.views import set_rollback


class CustomAPIException(Exception):
    """业务异常类"""

    code = 500
    message = ''

    def __init__(self, code=None, message=None):
        super().__init__()
        if code is not None:
            self.code = code
        if message is not None:
            self.message = message


def error_response(code=0, message=None, data=None):
    """错误数据返回"""
    wrapped_data = {
        'code': code,
        'status': 'error',
        'message': message,
        'meta': settings.META_MSG,
        'data': data,
    }
    return JsonResponse(wrapped_data)


def exception_handler(exc, context):
    """异常处理"""
    print(context['request'].path)
    print('raise error')
    traceback.print_exc()
    # trace_back = traceback.format_exc()
    # request = context.get('request')
    # error_log = ErrorLogModel(name=exc.__repr__(),
    #                           api=request.__repr__().split(' ')[0] + " {} {}>".format(request.method, request.path),
    #                           detail=trace_back,
    #                           data=request.data,
    #                           query_params=request.query_params)
    # error_log.save()
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    elif isinstance(exc, DRFPermissionDenied):
        req_path = ''.join(re.compile('\\D+').findall(context['request'].path))
        req_path = req_path[:-1] if req_path.endswith('/') else req_path
        temp_list = req_path.split('/')
        temp_list.pop(2)
        req_path = '/'.join(temp_list)
        hints = UnauthorizedHint.get(req_path, '')
        return error_response(status.HTTP_403_FORBIDDEN, '您没有{}权限'.format(hints))
        # return error_response(status.HTTP_403_FORBIDDEN, '您没有权限')
    if isinstance(exc, exceptions.NotAuthenticated):
        set_rollback()
        return error_response(status.HTTP_401_UNAUTHORIZED, exc.__class__.__name__)

    if isinstance(exc, CustomAPIException):
        # error_log.name += ':' + str(exc.code) + '_' + exc.message
        # error_log.save()
        set_rollback()
        return error_response(exc.code, exc.message)

    if isinstance(exc, exceptions.ValidationError):
        set_rollback()
        # return error_response(exc.status_code, next(iter(next(iter(exc.detail.values())))))
        print(exc.detail)
        print(dir(exc))
        print(exc.status_code)
        # message = {}
        # for key, errors in exc.detail.items():
        #     message[key] = []
        #     for desc in errors:
        #         message[key].append(desc)
        # return error_response(code=exc.status_code, message=message)

        messages = []
        for key, errors in exc.detail.items():
            errors = ' '.join(errors)
            # errors = '{}: {}'.format(key, errors)
            errors = errors.replace('This field', key).replace('This value', 'The value of ' + key).replace(
                'this field', key).replace('this value', 'value of' + key)
            messages.append(errors)
        return error_response(code=exc.status_code, message=' '.join(messages))

        # msg = [i for i in exc.detail]
        # print(msg)

    if isinstance(exc, exceptions.APIException):
        set_rollback()
        return error_response(exc.status_code, exc.__class__.__name__)

    return None

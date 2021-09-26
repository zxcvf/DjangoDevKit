# import base64
# import time
# from urllib import parse
#
# from rest_framework import status
# from rest_framework.exceptions import APIException
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
#
# import rpc
# from utils.remote_function.obbyauth_pb2 import VerifyJWTRequest
# from utils.remote_function.obbyauth_pb2_grpc import AuthStub
#
#
# class AuthenticationFailed(APIException):
#     status_code = status.HTTP_401_UNAUTHORIZED
#     default_detail = '请登录'
#     default_code = 'authentication_failed'
#
#
# def remote_authentic(jwt, userModel=User):
#     """
#     :return:
#     """
#     msg = VerifyJWTRequest(jwt=jwt)
#     resp = rpc.run(AuthStub, msg, 'Verify')
#     print('Decoded JWT:', resp)
#     if resp.get('errmsg'):
#         return
#     return User(resp)
#
#
# def obby_user_authentic(jwt_value):
#     user = remote_authentic(jwt_value)
#     if not user:
#         raise AuthenticationFailed
#     return user, None
#
#
# def other_dispatcher(raw_header, jwt_value):
#     # todo 增加新验证途径
#     header = dict(parse.parse_qsl(str(raw_header[2], encoding="utf-8")))
#     # header = {
#     #    * "RN": "pub",   Resource Namespace
#     #     "action": "POST",    可根据不同需求 构造不同的参数
#     #     "": ""
#     #     ...
#     # }
#
#     # H5 家长端
#     if header.get('RN') == 'ParentAPI':
#         phone_num = base64.b64decode(raw_header[3])
#         # id: 1,1,1  parent_id,student_id,school_id        修改为condition更保密
#         return Parent.init(phone_num=phone_num, condition=header.get('condition')), None
#     # H5 教师端
#     elif header.get('RN') == 'TeacherAPI':
#         # phone_num = base64.b64decode(raw_header[3])
#         auth_user, _ = obby_user_authentic(raw_header[1])
#         # id: 1,1,1  parent_id,student_id,school_id        修改为condition更保密
#         return Teacher.init(auth_user=auth_user,
#                             condition=header.get('condition')), None
#     # Web 员工端
#     elif header.get('RN') == 'StaffAPI':
#         auth_user, _ = obby_user_authentic(raw_header[1])
#         return SaasUser.init(raw_header=raw_header,
#                              auth_user=auth_user,
#                              condition=header.get('condition')), None
#
#     # elif header.get('RN') startwith 'obbycode'... :
#     #     pass
#
#     print('AnonymousUser')
#     return AnonymousUser({raw_header[0]: raw_header[1]}), None  # 游客
#
#
# class RemoteAuthentication(JSONWebTokenAuthentication):
#     """
#     verify jwt-token to obbyauth
#     """
#
#     def auth_dispatcher(self, jwt_value, header):
#         """ 将不同命名空间的验证头分发到不同验证器 """
#         # 如果Authorization!=jwt {token}, 那么jwt_value将为空， header将为[jwt, {token}]
#         # 如果Authorization=jwt {token}, 那么jwt_value将为{token}， header将为[jwt, {token}]
#         if len(header) == 2:  # Authorization = jwt {}
#             # 这里为django的默认jwt, 请求中台
#             return obby_user_authentic(jwt_value)
#
#         elif len(header) > 2:  # Authorization = other
#             # 这里不为django的默认jwt, 请自行验证
#             return other_dispatcher(header, jwt_value)
#
#         elif jwt_value is None and not header:
#             # 这里为django不传验证头情况  Authorization = None
#             return BlankUser({}), None
#
#         else:  # 无满足情况
#             raise AuthenticationFailed
#
#     def authenticate(self, request):
#         from rest_framework.authentication import get_authorization_header
#         header = get_authorization_header(request).split()
#         jwt_value = header[1] if header else None
#         print('header: {}'.format(header))
#         return self.auth_dispatcher(jwt_value, header)

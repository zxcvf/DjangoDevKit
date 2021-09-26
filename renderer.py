from django.conf import settings
from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    """自定义JSON返回数据"""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        wrapped_data = {
            'code': 200,
            'status': 'success',
            'message': '',
            'meta': settings.META_MSG,
            'data': data,
        }
        return super().render(wrapped_data, accepted_media_type, renderer_context)



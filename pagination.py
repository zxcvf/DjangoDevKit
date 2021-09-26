from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class CustomPageNumberPagination(PageNumberPagination):
    """自定义翻页类"""

    max_page_size = 100
    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('pagination', OrderedDict([
                ('page', self.page.number),
                ('size', self.page.paginator.per_page),
                ('total', self.page.paginator.count),
                ('last', self.page.paginator.num_pages)
            ])),
            ('content', data)
        ]))

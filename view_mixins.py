from rest_framework import status
from rest_framework.response import Response


class RetrieveModelMixin:
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)


class ListModelMixin:
    """
    List a queryset.
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class ListWithoutPaginateMixin:
    """ List a queryset without paginate. """

    def list_all(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class CreateWithSerializerMixin:
    """ 使用单独的create_serializer_class 来序列化请求数据 """
    create_serializer_class = None

    def create(self, request, *args, **kwargs):
        """新建接口"""
        serializer = self.create_serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(serializer.validated_data)
        if isinstance(instance, list):
            return Response(self.get_serializer(instance, many=True).data)
        return Response(self.get_serializer(instance).data)


class UpdateWithSerializerMixin:
    """类似mixin里的Update类，区别在于这里使用单独的serializer来序列化请求数据"""

    update_serializer_class = None

    def update(self, request, *args, **kwargs):
        """ 编辑接口 """

        instance = self.get_object()
        serializer = self.update_serializer_class(
            instance,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(self.get_serializer(instance).data)


class PartialUpdateWithSerializerMixin:
    """ 局部更新类似mixin里的Update类，区别在于这里使用单独的serializer来序列化请求数据"""
    update_serializer_class = None

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.update_serializer_class(
            instance,
            data=request.data,
            context={'request': request},
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class DestroyModelMixin:
    """ Destroy a model instance. """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response('删除成功', status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class RetrieveWithSerializerModelMixin:
    """
    Retrieve a model instance with special serializer for retrieving.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        context = {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
        }
        serializer = self.retrieve_serializer_class(instance, context=context)
        return Response(serializer.data)

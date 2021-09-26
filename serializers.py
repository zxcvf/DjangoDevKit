from abc import ABC

from rest_framework import serializers
from rest_framework.serializers import LIST_SERIALIZER_KWARGS, ListSerializer


class BaseModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        super().__init__(*args, **kwargs)

        if exclude is not None:
            excluded = set(exclude)
            for field_name in excluded:
                self.fields.pop(field_name)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class DataSerializer(serializers.Serializer):
    """只用户请求数据序列化"""

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class EmptySerializer(DataSerializer):
    """ 无字段 """


class ForeignKeyField:
    pass


class VirtualUserField:
    pass


class VirtualUserModel:
    pass


class CountListSerializer(ListSerializer, ABC):
    """ 给listSerializer增加一个排序属性, child 在many=True时的渲染过程会增加一个order """

    def to_representation(self, data):
        from django.db import models
        iterable = data.all() if isinstance(data, models.Manager) else data
        ret = []
        for order, item in enumerate(iterable):
            self.child.order = order
            ret.append(self.child.to_representation(item))
        return ret


class CountListSerializerMixin:
    """ 集成Mixin覆盖原有的ListSerializer使用CountListSerializer新增一个排序属性 """

    @classmethod
    def many_init(cls, *args, **kwargs):
        allow_empty = kwargs.pop('allow_empty', None)
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {
            'child': child_serializer,
        }
        if allow_empty is not None:
            list_kwargs['allow_empty'] = allow_empty
        list_kwargs.update({
            key: value for key, value in kwargs.items()
            if key in LIST_SERIALIZER_KWARGS
        })
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', CountListSerializer)
        return list_serializer_class(*args, **list_kwargs)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """支持动态指定字段的序列化器，传参fields，序列化和反序列化都支持"""
    Meta: type

    def __init__(self, *args, **kwargs):
        """支持字段动态生成的序列化器，从默认的Meta.fields中过滤，无关字段不查不序列化"""
        fields = kwargs.pop('fields', None)
        exclude_fields = kwargs.pop('exclude_fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None and fields != '__all__':
            allow = set(fields)
            existing = set(self.fields)
            for f in existing - allow:
                self.fields.pop(f)
        if exclude_fields is not None:
            existing = set(self.fields)
            exclude = set(exclude_fields)
            for f in existing & exclude:
                self.fields.pop(f)

    def __new__(cls, *args, **kwargs):
        """
        list序列化时，首先使用传参的fields，默认用meta.list_fields作为序列化字段
        如果传参用的exclude_fields, 会使用set(fields) - set(exclude_fields)
        """
        exclude_fields = kwargs.pop('exclude_fields', [])
        if kwargs.pop('many', False):
            list_fields = getattr(cls.Meta, 'list_fields', None)
            if exclude_fields and 'fields' not in kwargs:
                kwargs['fields'] = set(getattr(cls.Meta, 'fields', [])) - set(exclude_fields)
            if list_fields and 'fields' not in kwargs:
                kwargs['fields'] = list_fields
            return cls.many_init(*args, **kwargs)
        kwargs['fields'] = set(getattr(cls.Meta, 'fields', [])) - set(exclude_fields)
        print(kwargs)
        return super().__new__(cls, *args, **kwargs)

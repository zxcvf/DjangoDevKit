import ctypes

from rest_framework.serializers import SerializerMetaclass


class Node:
    def __init__(self, condition=None, data=None, id=None, parent=None, instance=None, Model=None, serializer=None,
                 children=None):
        if children is None:
            children = []
        self.condition = condition  # str: parent.parent.index, parent.index,index
        self.id = id  # str:  parent.parent.id, parent.id,id
        self.parent = parent  # Node

        self.data = data  # info 信息 serializer.data等
        self.instance = instance  # ORM instance
        self.Model = Model  # 节点的Model
        self.serializer = serializer  # 序列化, 填入django 序列化， 或者任意返回data型的函数   data和serializer填入一个就行
        self.children = children if children else []  # Nodes
        self.set_data()

    def __repr__(self):
        return '<id={}, condition={}, Model={}>'.format(self.id, self.condition, self.Model)

    def set_data(self):
        """ 将节点转换为json， 可扩展为接受任意自己写的序列化 """
        if self.data is not None:
            return
        if self.serializer:
            if isinstance(self.serializer, SerializerMetaclass):
                self.data = self.serializer(instance=self.instance).data
                return
            self.serializer(self)

    def add(self, node, idx: int = None):
        node.parent = self
        if idx is not None:
            return self.children.insert(idx, node)
        return self.children.append(node)

    def pop(self, idx: int = None):
        """ todo """

    def node_json(self):
        """ 当前节点的JSON格式 """
        return {
            'condition': self.condition,
            'id': self.id,
            'data': self.data,  # 使用自定义序列化，
            'model': self.Model.__name__,
        }

    def json(self):
        """ 当前节点、子节点的JSON格式 """
        result = self.node_json()
        result['children'] = []
        for node in self.children:
            result['children'].append(node.json())
        return result


class FreeTree:
    def __init__(self, root: Node):
        self.root = root
        self.data = {}

    def json(self):
        return self.root.json()

    def __repr__(self):
        #  todo 使用self.json
        # return self.json()
        return '<tree root={}-{}>'.format(self.root.Model, self.root.id)

    def search(self, condition):
        # 输入子节点condition  ps: 0,0,0  todo 不在树内进行format
        indexes = list(map(lambda x: int(x), condition.split(',')))
        cursor = self.root
        for i in indexes[1:]:
            cursor = cursor.children[i]
        return cursor

    def condition_nodes(self, condition):
        # 遍历condition 从root开始, 返回相关所有Node
        indexes = list(map(lambda x: int(x), condition.split(',')))
        cursor = self.root
        yield cursor
        for i in indexes[1:]:
            cursor = cursor.children[i]
            yield cursor

    # todo 加一个只渲染只加载子树
    # todo 创建完树后存入缓存(仅存入地址 保证修改同步安全性
    # address = id(value)  # 获取value的地址，赋给address
    # value = ctypes.cast(address, ctypes.py_object).value  # 读取地址中的变量


def list_condition_nodes(iter_, len_=None):
    # 遍历condition 从root开始, 返回相关所有Node, 长度不到补None
    ret = []
    for i in iter_:
        ret.append(i)
    if len_:
        ret.extend([None for i in range(len_ - len(ret))])
    return ret

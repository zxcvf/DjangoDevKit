import xlwt
from django.http import HttpResponse
from django.utils import timezone
from django.utils.encoding import smart_str, escape_uri_path
from rest_framework import serializers


class ExcelHelper:
    def __init__(self, filename=None, head=None, tag=False):
        """
        @param: filename, 打开的文件名 （ 暂时没有写打开文件， 默认创建名为Sheet 1的sheet，且不支持sheet切换
        @head: 列头
        @tag: 是否需要在第一行加上导出时间
        """

        self._workbook = xlwt.Workbook(encoding='utf-8')
        self._index = 0
        self._sheet = self._workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
        self._row = self._sheet.row(0)
        if tag:
            tag = ['导出时间：{}'.format(self.get_tag_time())]
            self.append_row(tag)
        if head:
            self.append_row(head)

    def set_row(self, column, values):
        row = self._sheet.row(column)
        for i, value in enumerate(values):
            row.write(column, value)

    def _set_next_row(self):
        self._index += 1
        self._row = self._sheet.row(self._index)

    def append_row(self, values: list):
        """
        新增一行
        """
        for i, value in enumerate(values):
            self._row.write(i, value)
        self._set_next_row()

    def append_rows(self, values_list: list):
        """
        @param values_list 二维数组
        新增多行
        """
        for values in values_list:
            self.append_row(values)

    def pop_row(self):
        """
        删除最后一行
        """

    def export_response(self, filename):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        self._workbook.save(response)
        response['Access-Control-Expose-Headers'] = 'content-disposition'
        response["Content-Disposition"] = "attachment;filename*=UTF-8''{}".format(escape_uri_path(filename))
        return response

    def export_local(self, path, filename):
        """
        导出到本地
        """

    def get_tag_time(self):
        serializer = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
        return serializer.to_representation(timezone.now())

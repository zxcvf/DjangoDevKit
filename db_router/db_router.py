from pprint import pprint

from django.conf import settings
from django.db import connections
from threadlocals.threadlocals import get_request_variable

DB_USING = 'dbConnection'
DB_ROUTE = 'org'

DBS = [None, *DATABASES.keys()]

print('load DefaultRouter')


class DefaultRouter:
    def check_db(self):
        pass

    label_prefix = '{}{}'.format(
        getattr(settings, 'DYNAMIC_DATABASES_PREFIX', 'DYNAMIC_DATABASE'),
        getattr(settings, 'DYNAMIC_DATABASES_SEPARATOR', '_')
    )

    def return_db(self, model, **hints):
        url_pram = get_request_variable(DB_USING)

        if model._meta.app_label.startswith(self.label_prefix):
            return model._meta.app_label
        return url_pram

    def db_for_read(self, model, **hints):
        return self.return_db(model, **hints)

    def db_for_write(self, model, **hints):
        return self.return_db(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return None

# class DefaultRouter:
#     def get_db(self):
#         db = get_request_variable(DB_USING)
#         return db
#
#     def check_db(self, db):
#         """ implement your Exception"""
#         if db not in DBS:
#             raise Exception
#         return db
#
#     def db_for_read(self, model, **hints):
#         db = self.get_db()
#         return self.check_db(db)
#
#     def db_for_write(self, model, **hints):
#         db = self.get_db()
#         return self.check_db(db)
#
#     def allow_relation(self, obj1, obj2, **hints):
#         db = self.get_db()
#         return self.check_db(db)
#
#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         db = self.get_db()
#         return self.check_db(db)

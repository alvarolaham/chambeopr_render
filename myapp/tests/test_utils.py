"""
This is test_utils.py
"""

from django.db import connections
from django.test.runner import DiscoverRunner


class PostgresTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serialize = kwargs.get("serialize", True)

    def setup_databases(self, **kwargs):
        old_config = super().setup_databases(**kwargs)
        for alias in connections:
            connection = connections[alias]
            with connection.cursor() as cursor:
                cursor.execute("SET session_replication_role = 'replica';")
        return old_config

    def teardown_databases(self, old_config, **kwargs):
        for alias in connections:
            connection = connections[alias]
            with connection.cursor() as cursor:
                cursor.execute("SET session_replication_role = 'origin';")
        super().teardown_databases(old_config, **kwargs)

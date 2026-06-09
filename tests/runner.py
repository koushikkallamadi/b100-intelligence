from django.test.runner import DiscoverRunner

class UnmanagedModelsTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        # Dynamically set managed=True for all models so they are created in SQLite test DB
        from django.apps import apps
        for model in apps.get_models():
            if not model._meta.managed:
                model._meta.managed = True
        return super().setup_databases(**kwargs)

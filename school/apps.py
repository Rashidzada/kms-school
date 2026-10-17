from django.apps import AppConfig


class SchoolConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "school"

    def ready(self):
        import sys

        # Prevent LogEntry sequence collision from ever crashing Django Admin
        try:
            from django.contrib.admin.models import LogEntryManager

            orig_log_actions = LogEntryManager.log_actions

            def safe_log_actions(self, *args, **kwargs):
                try:
                    return orig_log_actions(self, *args, **kwargs)
                except Exception:
                    # If duplicate key or sequence collision occurred, auto-sync all sequences and retry once
                    try:
                        from school.backup_utils import sync_all_postgresql_sequences

                        sync_all_postgresql_sequences()
                        return orig_log_actions(self, *args, **kwargs)
                    except Exception:
                        return None

            LogEntryManager.log_actions = safe_log_actions
        except Exception:
            pass

        # Automatically sync sequences after any migrations
        from django.db.models.signals import post_migrate

        def on_post_migrate(**kwargs):
            try:
                from school.backup_utils import sync_all_postgresql_sequences

                sync_all_postgresql_sequences()
            except Exception:
                pass

        post_migrate.connect(on_post_migrate, sender=self)

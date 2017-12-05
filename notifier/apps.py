# on each start up, create notification emails
# TODO do this via migrations?? So no stress starting up the app

from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migration_callback(sender, **kwargs):
    from notifier.management import create_notifications, create_backends
    create_backends(app='notifier')
    create_notifications(app='notifier')


class NotifierConfig(AppConfig):
    name = 'notifier'

    def ready(self):
        post_migrate.connect(post_migration_callback, sender=self)

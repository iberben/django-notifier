# on each start up, create notification emails
# TODO do this via migrations?? So no stress starting up the app

from django.apps import AppConfig


class NotifierConfig(AppConfig):
    name = 'notifier'

    def ready(self):
        from notifier.management import create_notifications, create_backends

        create_backends(app='notifier')
        create_notifications(app='notifier')

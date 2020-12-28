###############################################################################
# Imports
###############################################################################
# Python
from smtplib import SMTPException

import logging

# Django
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string

from premailer import transform


###############################################################################
# Code
###############################################################################
class BaseBackend(object):
    # Name of backend method associated with this class
    name = None
    display_name = None
    description = None

    def __init__(self, notification, *args, **kwargs):
        self.notification = notification
        self.template = (
            '/notifier/%s/%s.txt' %
            (notification.name, self.name)
        )

    # Define how to send the notification
    def send(self, user, context=None):
        if not context:
            self.context = {}
        else:
            self.context = context

        self.context.update({
            'user': user,
            'site': Site.objects.get_current() if settings.SITE_ID else None
        })

    def send_anonymous(self, to, context=None):
        """
        Send an email to just an email address.
        """
        return False


class EmailBackend(BaseBackend):
    name = 'email'
    display_name = 'Email'
    description = 'Send via email'

    def __init__(self, notification, *args, **kwargs):
        super(EmailBackend, self).__init__(notification, *args, **kwargs)

        self.template_subject = (
            'notifier/%s/%s_subject.txt' % (notification.name, self.name)
        )
        self.template_text_message = (
            'notifier/%s/%s_text_message.txt' % (notification.name, self.name)
        )
        self.template_html_message = (
            'notifier/%s/%s_html_message.html' % (notification.name, self.name)
        )

    def send(self, user, context=None):
        super(EmailBackend, self).send(user, context)

        subject = render_to_string(
            self.template_subject,
            self.context
        )
        subject = ''.join(subject.splitlines())
        text_message = render_to_string(
            self.template_text_message,
            self.context
        )
        html_message = transform(
            html=render_to_string(
                self.template_html_message,
                self.context
            ),
            strip_important=False,
            keep_style_tags=True,
            cssutils_logging_level=logging.CRITICAL
        )

        try:
            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email, ],
                html_message=html_message
            )
        except SMTPException:
            return False
        else:
            return True

    def send_anonymous(self, to, context=None):
        """
        Send an email to just an email address.
        """
        if not context:
            self.context = {}
        else:
            self.context = context
            self.context.update({
                'site': Site.objects.get_current()
                if settings.SITE_ID else None
            })

        subject = render_to_string(
            self.template_subject,
            self.context
        )
        subject = ''.join(subject.splitlines())
        text_message = render_to_string(
            self.template_text_message,
            self.context
        )
        html_message = transform(
            html=render_to_string(self.template_html_message, context),
            strip_important=False,
            keep_style_tags=True,
            cssutils_logging_level=logging.ERROR,
        )

        try:
            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to, ],
                html_message=html_message
            )
        except SMTPException:
            return False
        else:
            return True

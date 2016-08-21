import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.sites.models import Site


def sender(template_prefix):
    ''' Creates a function called `send_email` '''

    def send_email(to, kind, **kwargs):
        ''' Sends an e-mail to the given address.

        to: The address
        kind: the ID for an e-mail kind; it should point to a subdirectory of
            %(template_prefix)s containing subject.txt and message.html, which
            are django templates for the subject and HTML message respectively.

        context: a context for rendering the e-mail.

        ''' % {"template_prefix": template_prefix}

        return __send_email__(template_prefix, to, kind, **kwargs)

    return send_email


send_email = sender("symposion/emails")


def __send_email__(template_prefix, to, kind, **kwargs):

    current_site = Site.objects.get_current()

    ctx = {
        "current_site": current_site,
        "STATIC_URL": settings.STATIC_URL,
    }
    ctx.update(kwargs.get("context", {}))
    subject_template = os.path.join(template_prefix, "%s/subject.txt" % kind)
    message_template = os.path.join(template_prefix, "%s/message.html" % kind)
    subject = "[%s] %s" % (
        current_site.name,
        render_to_string(subject_template, ctx).strip()
    )

    message_html = render_to_string(message_template, ctx)
    message_plaintext = strip_tags(message_html)

    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        bcc_email = settings.ENVELOPE_BCC_LIST
    except AttributeError:
        bcc_email = None

    email = EmailMultiAlternatives(subject, message_plaintext, from_email, to, bcc=bcc_email)
    email.attach_alternative(message_html, "text/html")
    email.send()

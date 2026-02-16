import ssl

from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend
from django.core.mail.utils import DNS_NAME


class CustomEmailBackend(DjangoEmailBackend):
    """
    Custom SMTP backend compatible with Python 3.12+.

    Django 3.1.4 passes keyfile/certfile to smtplib.SMTP_SSL() and
    SMTP.starttls(), but Python 3.12 removed those parameters.
    This backend uses an ssl.SSLContext instead.
    """

    def open(self):
        if self.connection:
            return False

        connection_params = {"local_hostname": DNS_NAME.get_fqdn()}
        if self.timeout is not None:
            connection_params["timeout"] = self.timeout

        try:
            self.connection = self.connection_class(
                self.host, self.port, **connection_params
            )

            if not self.use_ssl and self.use_tls:
                context = ssl.create_default_context()
                self.connection.starttls(context=context)

            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise

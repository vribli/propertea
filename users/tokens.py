import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    This class seeks to generate tokens for activation emails.
    """
    def _make_hash_value(self, user, timestamp):
        """
        This method seeks to generate tokens for activation emails.

        :param user: The User associated with the request.
        :param timestamp: The timestamp associated with the request
        :return: The token used for activation emails for the particular user at the particular timestamp.
        """
        return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.profile.signup_confirmation)
        )


account_activation_token = AccountActivationTokenGenerator()

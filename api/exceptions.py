"""
This module provides a custom exceptions for the api app.
"""

from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import viewsets

"""
                        API EXCEPTIONS
"""


class PaymentRequired(APIException):
    """
    Return a HTTP_402_PAYMENT_REQUIRED.
    """
    status_code = 402
    default_detail = 'Payment is required for access to this resource.'

"""
                        VIEW SETS
"""


class PaymentRequiredViewSet(viewsets.GenericViewSet):
    """
    Define the `initial` method.
    """

    def initial(self, request, *args, **kwargs):
        """
        Raise `PaymentRequired` if user profile is not enabled.
        """
        user = request.user
        if hasattr(user, 'nationals'):
            if user.nationals.enabled is not True:
                raise PaymentRequired()
        elif hasattr(user, 'administrator'):
            if user.administrator.enabled is not True:
                raise PaymentRequired()
        elif hasattr(user, 'host'):
            if user.host.enabled is not True:
                raise PaymentRequired()
        super(PaymentRequiredViewSet, self).initial(request, *args, **kwargs)


"""
                        API EXCEPTION HANDLER
"""

def api_exception_handler(exc, context):
    """
    Insert the `status_code` into the error message. Also, define a usage
    for all custom exceptions.
    """
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response


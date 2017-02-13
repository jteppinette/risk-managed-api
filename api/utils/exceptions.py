"""
This module provides a custom exceptions for the api app.
"""

from rest_framework.views import exception_handler

"""
                        API EXCEPTION HANDLER
"""

def api_exception_handler(exc):
    """
    Insert the `status_code` into the error message. Also, define a usage
    for all custom exceptions.
    """
    response = exception_handler(exc)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response


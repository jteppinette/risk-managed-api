"""
Asserts that the Water Dragon User Helpers endpoints are working properly.

The following tests can be executed with the following command.
    
    `coverage run --source='api' manage.py test api`

    This command will run all tests files in `api/tests/` and will generate a
    coverage report that can be seen by running `coverage -rm`.

Note:

    All testing commands need to executed from the directory containing
    `manage.py`.
"""

from rest_framework.test import APITestCase
from rest_framework import status

from unittest import skip

import json

# Custom User Model
from django.contrib.auth import get_user_model

def create_user(username, password):
    """
    Create a user given an username and password.
    """
    return get_user_model().objects.create_user(username=username,
                                                email=username+'@'+username+'.com',
                                                password=password)


class UserHelpersRestTests(APITestCase):
    """
    The following tests have been created to assert that the user helper model
    endpoints perform accurately and reliably.
    """
    
    """
                             USER HELPER MODELS
    """

    def test_admin_or_read_only(self):
        """
        `Organization` and `University` objects should be only editable to
        users with the option `is_superuser` set to True.
        """
        admin_user = create_user('josh', 'test')
        admin_user.is_superuser = True
        admin_user.save()

        user = create_user('ks', 'ks')

        self.client.login(username='josh', password='test')

        # Initial `Organizations` by admin
        response = self.client.post('/organizations/',
                                    {'name': 'Kappa Sigma'})
        response = self.client.post('/organizations/',
                                    {'name': 'Sigma Alpha Epsilon'})
        # Initial `Universities` by admin
        response = self.client.post('/universities/',
                                    {'name': 'Southern Polytechnic State University',
                                     'acronym': 'SPSU',
                                     'state': 'Georgia'})

        self.client.login(username='ks', password='ks')

        # Organization by non admin `User`
        response = self.client.post('/organizations/',
                                    {'name': 'Sigma Nu'})
        # University by non admin `User`
        response = self.client.post('/organizations/',
                                    {'name': 'Georgia Institute of Technology',
                                     'acronym': 'GT',
                                     'state': 'Georgia'})

        
        # Test for correct number of `Organizations`
        response = self.client.get('/organizations/')
        content = json.loads(response.content)['results']

        self.assertEquals(len(content), 2)
        self.assertIn('Kappa Sigma', str(content))

        # Test for correct number of `Universities`
        response = self.client.get('/universities/')
        content = json.loads(response.content)['results']

        self.assertEquals(len(content), 1)
        self.assertIn('Southern', str(content))

        # Clean up models
        admin_user.delete()
        user.delete()

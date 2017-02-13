"""
Asserts that the Water Dragon Email endpoints are working properly.

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


class EmailRestTests(APITestCase):
    """
    
    The following tests have been created to assert that the email 
    endpoints perform accurately and reliably.
    """

    def test_carbon_copy_address_by_admin(self):
        """
        Assert that when a `CarbonCopyAddress` is requested by an admin that
        all objects are returned.
        """
        # Create admin
        admin = create_user(username='josh', password='josh')
        admin.is_superuser = True
        admin.save()

        # Create `University`
        self.client.login(username='josh', password='josh')
        response = self.client.post('/universities/', {'name': 'Southern Poly',
                                                       'acronym': 'SPSU',
                                                       'state': 'Georgia'})
        spsu = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/', {'name': 'Georgia Tech',
                                                       'acronym': 'GT',
                                                       'state': 'Georgia'})
        gt = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)


        # Create `Administrator`
        response = self.client.post('/administrators/', {'username': 'spsu', 
                                                            'password': 'spsu',
                                                            'university': str(spsu['id'])})
        spsu_admin = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/administrators/', {'username': 'gt', 
                                                            'password': 'gt',
                                                            'university': str(gt['id'])})
        gt_admin = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)


        # Create `CarbonCopyAddresses`
        self.client.login(username='spsu', password='spsu')
        response = self.client.post('/carboncopyaddresses/',
                                    {'email': 'josheppinette@josheppinette.com'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self.client.login(username='gt', password='gt')
        response = self.client.post('/carboncopyaddresses/',
                                    {'email': 'josheppinette@josheppinette.com'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Test
        self.client.login(username='josh', password='josh')
        response = self.client.get('/carboncopyaddresses/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 2)

    def test_user_cannot_create_copy_for_another_user(self):
        """
        Assert that one user has no permissions on another user's
        `CarbonCopyAddresses`, including `POST`.
        """
        josh = create_user('josh', 'josh')
        brennan = create_user('brennan', 'brennan')

        self.client.login(username='josh', password='josh')
        response = self.client.post('/carboncopyaddresses/',
                                    {'email': 'bob@bob.com'})
        content = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(content['user'], josh.id)

    def test_user_can_only_delete_their_own_addresses(self):
        """
        Assert that a user only has delete rights on their own addresses.
        Also, that the user does not need to pass in the user.
        """
        josh = create_user('josh', 'josh')
        brennan = create_user('brennan', 'brennan')

        self.client.login(username='josh', password='josh')
        response = self.client.post('/carboncopyaddresses/',
                                    {'email': 'bob@bob.com'})
        bob = json.loads(response.content)

        self.client.login(username='brennan', password='brennan')
        response = self.client.post('/carboncopyaddresses/',
                                    {'email': 'joe@joe.com'})
        joe = json.loads(response.content)

        response = self.client.delete('/carboncopyaddresses/' +str(bob['id'])+ '/')
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete('/carboncopyaddresses/' +str(joe['id'])+ '/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

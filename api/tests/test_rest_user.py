"""
Asserts that the Water Dragon `UserViewSet` REST endpoint is working properly.

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


class UserRestTests(APITestCase):
    """
    The following tests have been created to assert that the custom user model
    endpoint performs accurately and reliably.
    """

    """
                             CUSTOM USER MODEL
    """

    def test_anonymous_403(self):
        """
        An anonymous user should receive a 403 status.
        """
        response = self.client.get('/users/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_retrospect(self):
        """
        A logged in user should only be able to see its own `User` object.
        """
        user = create_user('ksspsu', 'test')
        self.client.login(username='ksspsu', password='test')

        response = self.client.get('/users/')
        content = json.loads(response.content)['results']

        self.assertEquals(len(content), 1)
        self.assertEquals(content[0], {'id': user.id, 'username': user.username, 'profile': None})

        user.delete()

    def test_set_password(self):
        """
        A user should be able to set a new password via a patch request.
        """
        user = create_user('ksspsu', 'test')
        self.client.login(username='ksspsu', password='test')

        url = '/users/' + str(user.id) + '/'
        response = self.client.patch(url, {'password': 'bob'})

        self.client.logout()
        self.client.login(username='ksspsu', password='bob')

        # Grab the list of all `Users`
        response = self.client.get('/users/')
        content = json.loads(response.content)['results']

        self.assertEquals(len(content), 1)
        self.assertEquals(content[0], {'id': user.id, 'username': user.username, 'profile': None})

        user.delete()

    def test_user_cannot_delete_another_user(self):
        """
        Assert that a `User` cannot delete another `User`.
        """
        user = create_user('ksspsu', 'test')
        user2 = create_user('saespsu', 'test2')

        self.client.login(username='ksspsu', password='test')
        
        # Attempt to delete user2 from user's account
        url = '/users/' + str(user2.id) + '/'
        response = self.client.delete(url)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username='saespsu', password='test2')

        # Attempt to delete user2 from user2's account
        url = '/users/' + str(user2.id) + '/'
        response = self.client.delete(url)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Create an admin account
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()
        self.client.login(username='josh', password='josh')

        # View all `User` objects to see that no deletes took place
        response = self.client.get('/users/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 3)

        # Clean up models
        admin.delete()
        user.delete()
        user2.delete()

    def test_only_admins_can_delete_users(self):
        """
        Assert that the only type of `User` that can delete other `Users` are
        `is_superuser`.
        """
        user = create_user('ksspsu', 'ksspsu')
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        self.client.login(username='ksspsu', password='ksspsu')

        # Attempt to delete `User` from non admin `User`
        response = self.client.delete('/users/' + str(user.id) + '/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username='josh', password='josh')

        # Delete `User` from admin `User`
        response = self.client.delete('/users/' + str(user.id) + '/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # Clean up models
        admin.delete()

    def test_can_login(self):
        """
        Asser that a user can login.
        """
        user = create_user('ksspsu', password='ksspsu')

        response = self.client.post('/login/',
                                    {'username': 'ksspsu',
                                     'password': 'ksspsu'})
        content = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Test logged in
        response = self.client.get('/users/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 1)

    def test_bad_login(self):
        """
        Assert that a bad login raises the correct exception
        """
        user = create_user('ksspsu', password='ksspsu')

        response = self.client.post('/login/',
                                    {'username': 'ksspsu',
                                     'password': 'ksspsjjjjjju'})
        content = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Incorrect authentication credentials', str(content))

    def test_can_logout(self):
        """
        Asser that a user can logout.
        """
        user = create_user('ksspsu', password='ksspsu')

        response = self.client.post('/login/',
                                    {'username': 'ksspsu',
                                     'password': 'ksspsu'})
        content = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Test logged in
        response = self.client.get('/users/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 1)

        # Logout
        response = self.client.get('/logout/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Test logged out
        response = self.client.get('/users/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

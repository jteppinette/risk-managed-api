"""
Asserts that the Water Dragon User Profile endpoints are working properly.

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


class UserProfileRestTests(APITestCase):
    """
    The following tests have been created to assert that each of the user
    profile rest endpoints perform accurately and reliably.
    """

    """
                             USER PROFILE MODELS
    """

    def test_create_user_profile_creates_user(self):
        """
        Assert that a `POST` request to one of the three user models requires
        an `username` and `password`. These two extra fields will be used to
        create a related `User` object.
        """
        # Create test data | Organization and University
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        self.client.login(username='josh', password='josh')

        response = self.client.post('/organizations/',
                                    {'name': 'Kappa Sigma'})
        kappa_sigma = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                    {'name': 'University of Georgia', 'acronym': 'UGA', 'state': 'Georgia'})
        uga = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
    
        # Create `Nationals` object
        self.client.logout()
        data = {'username': 'ks', 'password': 'ks',
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/nationals/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        nationals_user_id = json.loads(response.content)['user']

        # Assert that the `User` object matches
        self.client.login(username='ks', password='ks')
        response = self.client.get('/users/')
        content = json.loads(response.content)['results'][0]
        self.assertEquals(content['id'], nationals_user_id)

    def test_user_profile_change_user_information(self):
        """
        Assert that the api user can patch the user information connected to a
        user profile by sending a `PATCH` request to the user profile
        endpoint.
        """
        # Create test data | Organization and University
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        self.client.login(username='josh', password='josh')

        response = self.client.post('/organizations/',
                                    {'name': 'Kappa Sigma'})
        kappa_sigma = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                {'name': 'University of Georgia', 'acronym': 'UGA', 'state': 'Georgia'})
        uga = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
    
        # Create `Nationals` object
        self.client.logout()
        data = {'username': 'ks', 'password': 'ks',
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/nationals/', data)
        nationals_id = json.loads(response.content)['id']
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Login as new `Nationals` user
        self.client.login(username='ks', password='ks')

        # Edit password
        url = '/nationals/' + str(nationals_id) + '/'
        response = self.client.patch(url, {'password': 'bob'})

        # Login with new password
        result = self.client.login(username='ks', password='bob')
        self.assertEquals(result, True)
        
        # Edit username
        response = self.client.patch(url, {'username': 'ksnew'})

        # Login with new username
        result = self.client.login(username='ksnew', password='bob')
        self.assertEquals(result, True)

    def test_enabled_is_read_only(self):
        """
        The field `enabled` should not be able to be edited through the rest
        api. These should be edited by the `admin` through the admin site.
        """
        # Create test data | Organization and University
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        self.client.login(username='josh', password='josh')

        response = self.client.post('/organizations/',
                                    {'name': 'Kappa Sigma'})
        kappa_sigma = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                {'name': 'University of Georgia', 'acronym': 'UGA', 'state': 'Georgia'})
        uga = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
    
        # Create `Nationals` object
        self.client.logout()
        data = {'username': 'ks', 'password': 'ks',
                'organization': str(kappa_sigma['id']), 'enabled': True}
        response = self.client.post('/nationals/', data)
        content = json.loads(response.content)
        self.assertEquals(content['enabled'], False)

    def test_user_profile_username_is_unique(self):
        """
        Assert that when creating a new user profile the username must be unique.
        """
        # Create test data | Organization and University
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        self.client.login(username='josh', password='josh')
        response = self.client.post('/organizations/',
                                    {'name': 'Kappa Sigma'})
        kappa_sigma = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                    {'name': 'University of Georgia', 'acronym': 'UGA', 'state': 'Georgia'})
        uga = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
    
        # Create `Nationals` object
        self.client.logout()
        data = {'username': 'ks', 'password': 'ks',
                'organization': str(kappa_sigma['id']), 'enabled': True}
        response = self.client.post('/nationals/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create second `Nationals` object with the same username
        response = self.client.post('/nationals/', data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_is_superuser_or_no_delete(self):
        """
        User profiles should only be able to be deleted by `is_superuser`.
        """
        # Create test data | Organization and University
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        self.client.login(username='josh', password='josh')

        response = self.client.post('/organizations/',
                                    {'name': 'Kappa Sigma'})
        kappa_sigma = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                    {'name': 'University of Georgia', 'acronym': 'UGA', 'state': 'Georgia'})
        uga = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
    
        # Create `Nationals` object
        self.client.logout()
        data = {'username': 'ks', 'password': 'ks',
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/nationals/', data)
        nationals_id = json.loads(response.content)['id']
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Administrator` object
        data = {'username': 'uga', 'password': 'uga',
                'university': str(uga['id'])}
        response = self.client.post('/administrators/', data)
        administrator_id = json.loads(response.content)['id']
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Attempt delete by non admin
        self.client.login(username='ks', password='ks')
        response = self.client.delete('/nationals/'+str(nationals_id)+'/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete('/administrators/'+str(administrator_id)+'/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    """
                             NATIONALS
    """

    def test_nationals_viewset_by_anonymous(self):
        """
        The `Nationals` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `NationalsViewSet`.

        Assert that the when requested by an anonymous user the
        `NationalsViewSet` returns an empty list.
        """
        # Create Admin to create `Organization`
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        self.client.login(username='josh', password='josh')

        response = self.client.post('/organizations/',
                                    {'name': 'Kappa Sigma'})
        kappa_sigma = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Nationals` object
        self.client.logout()
        data = {'username': 'ks', 'password': 'ks',
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/nationals/', data)
        nationals_id = json.loads(response.content)['id']
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Perform request by anonymous
        response = self.client.get('/nationals/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nationals_viewset_by_admin(self):
        """
        The `Nationals` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `NationalsViewSet`.

        Assert that the when requested by an admin user the
        `NationalsViewSet` returns all objects.
        """
        # Create Admin to create `Organization`
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        self.client.login(username='josh', password='josh')

        response = self.client.post('/organizations/',
                                    {'name': 'Kappa Sigma'})
        kappa_sigma = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/organizations/',
                                    {'name': 'Sigma Alpha Epsilon'})
        sae = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)


        # Create `Nationals` objects
        self.client.logout()
        data = {'username': 'ks', 'password': 'ks',
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/nationals/', data)
        nationals_id = json.loads(response.content)['id']
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'sae', 'password': 'sae',
                'organization': str(sae['id'])}
        response = self.client.post('/nationals/', data)
        nationals_id = json.loads(response.content)['id']
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)


        # Perform request by admin
        self.client.login(username='josh', password='josh')
        response = self.client.get('/nationals/')
        content = json.loads(response.content)['results']
        self.assertIn('ks', str(content))
        self.assertIn('sae', str(content))

    def test_nationals_viewset_by_nationals(self):
        """
        The `Nationals` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `NationalsViewSet`.

        Assert that the when requested by a nationals user the
        `NationalsViewSet` returns itself.
        """
        # Create Admin to create `Organization`
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        self.client.login(username='josh', password='josh')

        response = self.client.post('/organizations/',
                                    {'name': 'Kappa Sigma'})
        kappa_sigma = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/organizations/',
                                    {'name': 'Sigma Alpha Epsilon'})
        sae = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)


        # Create `Nationals` objects
        self.client.logout()
        data = {'username': 'ks', 'password': 'ks',
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/nationals/', data)
        nationals_id = json.loads(response.content)['id']
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'sae', 'password': 'sae',
                'organization': str(sae['id'])}
        response = self.client.post('/nationals/', data)
        nationals_id = json.loads(response.content)['id']
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)


        # Perform request by admin
        self.client.login(username='sae', password='sae')
        response = self.client.get('/nationals/')
        content = json.loads(response.content)['results']
        self.assertIn('sae', str(content))
        self.assertEquals(len(content), 1)

    def test_nationals_viewset_by_host(self):
        """
        The `Nationals` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `NationalsViewSet`.

        Assert that the when requested by a host user the
        `NationalsViewSet` returns its nationals object.
        """
        # Create Admin
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        # Create `Organizations`
        self.client.login(username='josh', password='josh')
        response = self.client.post('/organizations/',
                                    {'name': 'Kappa Sigma'})
        kappa_sigma = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/organizations/',
                                    {'name': 'Sigma Alpha Epsilon'})
        sae = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        #Create `Universities`
        response = self.client.post('/universities/',
                                    {'name': 'Southern Poly',
                                     'acronym': 'SPSU',
                                     'state': 'Georgia'})
        spsu = json.loads(response.content)

        # Create `Nationals` objects
        self.client.logout()
        data = {'username': 'ks', 'password': 'ks',
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/nationals/', data)
        nationals_id = json.loads(response.content)['id']
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'sae', 'password': 'sae',
                'organization': str(sae['id'])}
        response = self.client.post('/nationals/', data)
        nationals_id = json.loads(response.content)['id']
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Host` object
        data = {'username': 'ksspsu', 'password': 'ksspsu',
                'organization': str(kappa_sigma['id']),
                'university': str(spsu['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Perform request by `Host`
        self.client.login(username='ksspsu', password='ksspsu')
        response = self.client.get('/nationals/')
        content = json.loads(response.content)['results']
        self.assertIn('ks', str(content))
        self.assertEquals(len(content), 1)

    """
                             ADMINISTRATOR
    """

    def test_administrator_viewset_by_admin(self):
        """
        The `Administrator` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `AdministratorViewSet`.

        Assert that the when requested by an admin the
        `AdministratorViewSet` returns all results.
        """
        # Create Admin
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        # Create `University` object
        self.client.login(username='josh', password='josh')
        response = self.client.post('/universities/',
                                    {'name': 'Southern Poly',
                                     'acronym': 'SPSU',
                                     'state': 'Georgia'})
        spsu = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                                    {'name': 'Georgia Tech',
                                     'acronym': 'GT',
                                     'state': 'Georgia'})
        gt = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Administrator` object
        self.client.logout()
        data = {'username': 'spsu', 'password': 'spsu',
                'university': str(spsu['id'])}
        response = self.client.post('/administrators/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'gt', 'password': 'gt',
                'university': str(gt['id'])}
        response = self.client.post('/administrators/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Perform request by admin
        self.client.login(username='josh', password='josh')
        response = self.client.get('/administrators/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 2)

    def test_administrator_viewset_by_administrator(self):
        """
        The `Administrator` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `AdministratorViewSet`.

        Assert that the when requested by an `Administrator` the
        `AdministratorViewSet` returns itself.
        """
        # Create Admin
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        # Create `University` object
        self.client.login(username='josh', password='josh')
        response = self.client.post('/universities/',
                                    {'name': 'Southern Poly',
                                     'acronym': 'SPSU',
                                     'state': 'Georgia'})
        spsu = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                                    {'name': 'Georgia Tech',
                                     'acronym': 'GT',
                                     'state': 'Georgia'})
        gt = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Administrator` object
        self.client.logout()
        data = {'username': 'spsu', 'password': 'spsu',
                'university': str(spsu['id'])}
        response = self.client.post('/administrators/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'gt', 'password': 'gt',
                'university': str(gt['id'])}
        response = self.client.post('/administrators/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Perform request by admin
        self.client.login(username='spsu', password='spsu')
        response = self.client.get('/administrators/')
        content = json.loads(response.content)['results']
        self.assertIn('spsu', str(content))
        self.assertEquals(len(content), 1)

    def test_administrator_viewset_by_host(self):
        """
        The `Administrator` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `AdministratorViewSet`.

        Assert that the when requested by a `Host` the
        `AdministratorViewSet` returns its `Administrator` object.
        """
        # Create Admin
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        # Create `Organization` object
        self.client.login(username='josh', password='josh')
        response = self.client.post('/organizations/', 
                                    {'name': 'Kappa Sigma'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        kappa_sigma = json.loads(response.content)

        # Create `University` object
        response = self.client.post('/universities/',
                                    {'name': 'Southern Poly',
                                     'acronym': 'SPSU',
                                     'state': 'Georgia'})
        spsu = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                                    {'name': 'Georgia Tech',
                                     'acronym': 'GT',
                                     'state': 'Georgia'})
        gt = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Administrator` object
        self.client.logout()
        data = {'username': 'spsu', 'password': 'spsu',
                'university': str(spsu['id'])}
        response = self.client.post('/administrators/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'gt', 'password': 'gt',
                'university': str(gt['id'])}
        response = self.client.post('/administrators/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Host` object
        data = {'username': 'ksspsu', 'password': 'ksspsu',
                'university': str(spsu['id']),
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Perform request by admin
        self.client.login(username='ksspsu', password='ksspsu')
        response = self.client.get('/administrators/')
        content = json.loads(response.content)['results']
        self.assertIn('spsu', str(content))
        self.assertEquals(len(content), 1)

    """
                             HOST
    """

    def test_host_viewset_by_admin(self):
        """
        The `Host` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `HostViewSet`.

        Assert that the when requested by an admin the
        `HostViewSet` returns all results.
        """
        # Create Admin
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        # Create `Organization` objects
        self.client.login(username='josh', password='josh')
        response = self.client.post('/organizations/', 
                                    {'name': 'Kappa Sigma'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        kappa_sigma = json.loads(response.content)

        response = self.client.post('/organizations/', 
                                    {'name': 'Sigma Alpha Epsilon'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        sae = json.loads(response.content)


        # Create `University` object
        response = self.client.post('/universities/',
                                    {'name': 'Southern Poly',
                                     'acronym': 'SPSU',
                                     'state': 'Georgia'})
        spsu = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                                    {'name': 'Georgia Tech',
                                     'acronym': 'GT',
                                     'state': 'Georgia'})
        gt = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Host` objects
        self.client.logout()
        data = {'username': 'ksspsu', 'password': 'ksspsu',
                'university': str(spsu['id']),
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'saespsu', 'password': 'saespsu',
                'university': str(gt['id']),
                'organization': str(sae['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Perform request by admin
        self.client.login(username='josh', password='josh')
        response = self.client.get('/hosts/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 2)

    def test_host_viewset_by_host(self):
        """
        The `Host` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `HostViewSet`.

        Assert that the when requested by an admin the
        `HostViewSet` returns itself.
        """
        # Create Admin
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        # Create `Organization` objects
        self.client.login(username='josh', password='josh')
        response = self.client.post('/organizations/', 
                                    {'name': 'Kappa Sigma'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        kappa_sigma = json.loads(response.content)

        response = self.client.post('/organizations/', 
                                    {'name': 'Sigma Alpha Epsilon'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        sae = json.loads(response.content)


        # Create `University` object
        response = self.client.post('/universities/',
                                    {'name': 'Southern Poly',
                                     'acronym': 'SPSU',
                                     'state': 'Georgia'})
        spsu = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                                    {'name': 'Georgia Tech',
                                     'acronym': 'GT',
                                     'state': 'Georgia'})
        gt = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Host` objects
        self.client.logout()
        data = {'username': 'ksspsu', 'password': 'ksspsu',
                'university': str(spsu['id']),
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'saespsu', 'password': 'saespsu',
                'university': str(spsu['id']),
                'organization': str(sae['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Perform request by admin
        self.client.login(username='ksspsu', password='ksspsu')
        response = self.client.get('/hosts/')
        content = json.loads(response.content)['results']
        self.assertIn('ksspsu', str(content))
        self.assertEquals(len(content), 1)

    def test_host_viewset_by_nationals(self):
        """
        The `Host` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `HostViewSet`.

        Assert that the when requested by a nationals the
        `HostViewSet` returns all of its hosts.
        """
        # Create Admin
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        # Create `Organization` objects
        self.client.login(username='josh', password='josh')
        response = self.client.post('/organizations/', 
                                    {'name': 'Kappa Sigma'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        kappa_sigma = json.loads(response.content)

        response = self.client.post('/organizations/', 
                                    {'name': 'Sigma Alpha Epsilon'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        sae = json.loads(response.content)


        # Create `University` object
        response = self.client.post('/universities/',
                                    {'name': 'Southern Poly',
                                     'acronym': 'SPSU',
                                     'state': 'Georgia'})
        spsu = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                                    {'name': 'Georgia Tech',
                                     'acronym': 'GT',
                                     'state': 'Georgia'})
        gt = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Nationals` object
        data = {'username': 'sae', 'password': 'sae',
                'organization': str(sae['id'])}
        response = self.client.post('/nationals/', data)
        sae_nat = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Host` objects
        self.client.logout()
        data = {'username': 'ksspsu', 'password': 'ksspsu',
                'university': str(spsu['id']),
                'organization': str(kappa_sigma['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'saespsu', 'password': 'saespsu',
                'university': str(spsu['id']),
                'organization': str(sae['id']),
                'nationals': str(sae_nat['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'saegt', 'password': 'saegt',
                'university': str(gt['id']),
                'organization': str(sae['id']),
                'nationals': str(sae_nat['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Perform request by sae nationals
        self.client.login(username='sae', password='sae')
        response = self.client.get('/hosts/')
        content = json.loads(response.content)['results']
        self.assertIn('spsu', str(content))
        self.assertIn('gt', str(content))
        self.assertEquals(len(content), 2)

    def test_host_viewset_by_administrator(self):
        """
        The `Host` viewset returns different results based on the user
        requesting the data. This is described in `api/views.py` in
        `HostViewSet`.

        Assert that the when requested by an administrator the
        `HostViewSet` returns all of its hosts.
        """
        # Create Admin
        admin = create_user('josh', 'josh')
        admin.is_superuser = True
        admin.save()

        # Create `Organization` objects
        self.client.login(username='josh', password='josh')
        response = self.client.post('/organizations/', 
                                    {'name': 'Kappa Sigma'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        kappa_sigma = json.loads(response.content)

        response = self.client.post('/organizations/', 
                                    {'name': 'Sigma Alpha Epsilon'})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        sae = json.loads(response.content)


        # Create `University` object
        response = self.client.post('/universities/',
                                    {'name': 'Southern Poly',
                                     'acronym': 'SPSU',
                                     'state': 'Georgia'})
        spsu = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/universities/',
                                    {'name': 'Georgia Tech',
                                     'acronym': 'GT',
                                     'state': 'Georgia'})
        gt = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Administrator` object
        data = {'username': 'spsu', 'password': 'spsu',
                'university': str(spsu['id'])}
        response = self.client.post('/administrators/', data)
        spsu_admin = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Host` objects
        self.client.logout()
        data = {'username': 'ksspsu', 'password': 'ksspsu',
                'university': str(spsu['id']),
                'organization': str(kappa_sigma['id']),
                'administrator': str(spsu_admin['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'saespsu', 'password': 'saespsu',
                'university': str(spsu['id']),
                'organization': str(sae['id']),
                'administrator': str(spsu_admin['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        data = {'username': 'saegt', 'password': 'saegt',
                'university': str(gt['id']),
                'organization': str(sae['id'])}
        response = self.client.post('/hosts/', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Perform request by sae administrator
        self.client.login(username='spsu', password='spsu')
        response = self.client.get('/hosts/')
        content = json.loads(response.content)['results']
        self.assertIn('sae', str(content))
        self.assertIn('ks', str(content))
        self.assertEquals(len(content), 2)

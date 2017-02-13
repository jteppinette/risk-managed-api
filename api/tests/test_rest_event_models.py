"""
Asserts that the Water Dragon Event Models endpoints are working properly.

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

# User Helper Models
from api.models import Organization, University

# User Profile Models
from api.models import Nationals, Administrator, Host

# Email Helper Models
from api.models import CarbonCopyAddress

# Event Models
from api.models import Event, Procedure, Invitee

def create_user(username, password):
    """
    Create a user given an username and password.
    """
    return get_user_model().objects.create_user(username=username,
                                                email=username+'@'+username+'.com',
                                                password=password)


class EventModelsTests(APITestCase):
    """
    
    The following tests have been created to assert that each of the event
    models rest endpoints perform accurately and reliably.
    """

    def setUp(self):
        """
        Apply fixture data to test case.
        """
        self.admin = create_user('josh', 'josh')
        self.admin.is_superuser = True
        self.admin.save()

        self.ks = Organization.objects.create(name='Kappa Sigma')
        self.spsu = University.objects.create(name='Southern Polytechnic State University',
                                              acronym='SPSU',
                                              state='Georgia')
        
        self.sae = Organization.objects.create(name='Sigma Alpha Epsilon')
        self.gt = University.objects.create(name='Georgia Institute of Technology',
                                            acronym='GT',
                                            state='Georgia')

        ks_nat_user = create_user('ks', 'ks')
        self.ks_nat = Nationals.objects.create(user=ks_nat_user,
                                               organization=self.ks,
                                               enabled=True)

        spsu_admin_user = create_user('spsu', 'spsu')
        self.spsu_admin = Administrator.objects.create(user=spsu_admin_user,
                                                       university=self.spsu,
                                                       enabled=True)

        sae_nat_user = create_user('sae', 'sae')
        self.sae_nat = Nationals.objects.create(user=sae_nat_user,
                                                organization=self.sae)

        gt_admin_user = create_user('gt', 'gt')
        self.gt_admin_user = Administrator.objects.create(user=gt_admin_user,
                                                          university=self.gt)

        ksspsu_user = create_user('ksspsu', 'ksspsu')
        self.ksspsu = Host.objects.create(user=ksspsu_user,
                                          organization=self.ks,
                                          university=self.spsu,
                                          enabled=True)

        saespsu_user = create_user('saespsu', 'saespsu')
        self.saespsu = Host.objects.create(user=saespsu_user,
                                          organization=self.sae,
                                          university=self.spsu,
                                          enabled=True)

        ksgt_user = create_user('ksgt', 'ksgt')
        self.ksgt = Host.objects.create(user=ksgt_user,
                                          organization=self.ks,
                                          university=self.gt,
                                          enabled=True)

        self.data = {
            'name': 'New Event',
            'description': 'My event.',
            'date': '2014-07-21',
            'time': '00:00:00.000000',
            'location': 'Chapter House',
            'planner_name': 'Joshua Taylor Eppinette',
            'planner_mobile': '7704016678',
            'planner_email': 'josh.eppinette@waterdragon.net',
            'president_email': 'pres@pres.com',
            'sober_monitors': 'Josh Eppinette',
            'expected_guest_count': 50,
            'exclusivity': 'Invitation Only',
            'alcohol_distribution': 'Mobile Cocktails',
            'entry': 'Yes',
            'entry_description': 'Front Door',
            'co_sponsored_description': 'With Kappa Delta'
        }

    
    """
                             EVENT
    """
    
    def test_events_post_by_host(self):
        """
        Assert that a `Host` can create an `Event`.
        """
        self.client.login(username='ksspsu', password='ksspsu')

        response = self.client.post('/events/', self.data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_events_get_by_admin(self):
        """
        Assert that an admin can `GET` all `Event` objects.
        """
        # Create `Event`
        self.client.login(username='ksspsu', password='ksspsu')

        response = self.client.post('/events/', self.data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self.client.login(username='josh', password='josh')
        response = self.client.get('/events/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 1)

    def test_events_post_only_by_host(self):
        """
        Assert that only a `Host` can post a new `Event`.
        """
        # Anonymous
        self.client.logout()
        response = self.client.post('/events/', self.data)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin
        self.client.login(username='josh', password='josh')
        response = self.client.post('/events/', self.data)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Nationals
        self.client.login(username='ks', password='ks')
        response = self.client.post('/events/', self.data)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Administrator
        self.client.login(username='spsu', password='spsu')
        response = self.client.post('/events/', self.data)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_get_post_only(self):
        """
        Assert that the only methods allowed on `/events/' are `GET` and
        `POST`.
        """
        self.client.login(username='ksspsu', password='ksspsu')
        response = self.client.post('/events/', self.data)
        content = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Attempt `PATCH`
        response = self.client.patch('/events/' + str(content['id']) + '/',
                                     {'name': 'New Name'})
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Attempt `PUT`
        response = self.client.put('/events/' + str(content['id']) + '/',
                                     self.data)
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


        # Attempt `DELETE`
        response = self.client.delete('/events/' + str(content['id']) + '/')
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_events_get_queryset(self):
        """
        Assert that the `Event` `get_queryset` method returns the proper
        queryset.
        """
        edited_data = self.data

        # Create `Events`
        edited_data['name'] = 'KSSPSU EVENT'
        self.client.login(username='ksspsu', password='ksspsu')
        response = self.client.post('/events/', edited_data)
        content = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        edited_data['name'] = 'SAESPSU EVENT'
        self.client.login(username='saespsu', password='saespsu')
        response = self.client.post('/events/', edited_data)
        content = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        edited_data['name'] = 'KSGT EVENT'
        self.client.login(username='ksgt', password='ksgt')
        response = self.client.post('/events/', edited_data)
        content = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Admin
        self.client.login(username='josh', password='josh')

        response = self.client.get('/events/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 3)

        # Nationals
        self.client.login(username='ks', password='ks')

        response = self.client.get('/events/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 2)

        # Host
        self.client.login(username='ksspsu', password='ksspsu')

        response = self.client.get('/events/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 1)

    def test_events_end_by_host(self):
        """
        Assert that a `Host` can end an event at a custom url.
        """
        self.client.login(username='ksspsu', password='ksspsu')

        # Create an `Event`
        response = self.client.post('/events/', self.data)
        content = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # End the `Event`
        response = self.client.post('/events/' + str(content['id']) + '/end/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Test as `Administrator`
        self.client.login(username='spsu', password='spsu')
        response = self.client.post('/events/' + str(content['id']) + '/end/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_payment_required(self):
        """
        Assert that any access to `Events` requires payment.
        """
        self.client.login(username='ksspsu', password='ksspsu')

        # Disable `Host`
        Host.objects.filter(user__username='ksspsu').update(enabled=False)

        # Create an `Event`
        response = self.client.post('/events/', self.data)
        content = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        # Enable `Host` for further tests
        Host.objects.filter(user__username='ksspsu').update(enabled=True)

    """
                             PROCEDURE
    """

    def test_procedure_read_only(self):
        """
        Assert that `Procedures` are read only. They can be read by all owning
        user profiles (Nationals, Administrators, Hosts).
        """
        self.client.login(username='ksspsu', password='ksspsu')

        # Create `Event`
        response = self.client.post('/events/', self.data)
        event_one = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Procedures`
        event = Event.objects.get(id=event_one['id'])
        proc_one = Procedure.objects.create(event=event,
                                            description='Interior Sweep')
        proc_two = Procedure.objects.create(event=event,
                                          description='Exterior Sweep')

        # Test owning `Nationals` can `GET`
        self.client.login(username='ks', password='ks')
        response = self.client.get('/procedures/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 2)

        # Test owning `Nationals` cannot `POST`
        response = self.client.post('/procedures/', {'event': event_one['id'],
                                                     'description': 'Interior Sweep'})
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test owning `Administrator` can `GET`
        self.client.login(username='spsu', password='spsu')
        response = self.client.get('/procedures/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 2)

        # Test owning `Host` can `GET`
        self.client.login(username='ksspsu', password='ksspsu')
        response = self.client.get('/procedures/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 2)

        # Test owning `Host` cannot `POST`
        response = self.client.post('/procedures/', {'event': event_one['id'],
                                                     'description': 'Interior Sweep'})
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test owning `Host` cannot `PUT`
        response = self.client.post('/procedures/' + str(proc_one.id) + '/',
                                    {'description': 'Exterior Sweep'})
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_procedure_read_only(self):
        """
        Assert that `Nationals` and `Administrators` can only interact with
        the correct subset of all `Procedures`.
        """
        # Create `Events`

        # KSSPSU
        self.client.login(username='ksspsu', password='ksspsu')

        response = self.client.post('/events/', self.data)
        ksspsu_event = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # SAESPSU
        self.client.login(username='saespsu', password='saespsu')

        response = self.client.post('/events/', self.data)
        saespsu_event = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # KSGT
        self.client.login(username='ksgt', password='ksgt')

        response = self.client.post('/events/', self.data)
        ksgt_event = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Procedures`
        event = Event.objects.get(id=ksspsu_event['id'])
        ksspsu_proc_1 = Procedure.objects.create(event=event,
                                                 description='Interior Sweep')
        ksspsu_proc_2 = Procedure.objects.create(event=event,
                                                 description='Exterior Sweep')

        event = Event.objects.get(id=saespsu_event['id'])
        saespsu_proc_1 = Procedure.objects.create(event=event,
                                                  description='Interior Sweep')
        saespsu_proc_2 = Procedure.objects.create(event=event,
                                                  description='Exterior Sweep')

        event = Event.objects.get(id=ksgt_event['id'])
        ksgt_proc_1 = Procedure.objects.create(event=event,
                                                  description='Interior Sweep')
        ksgt_proc_2 = Procedure.objects.create(event=event,
                                                 description='Exterior Sweep')

        # `GET` by `ks`
        self.client.login(username='ks', password='ks')
        response = self.client.get('/procedures/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 4)
        self.assertIn(str(ksgt_proc_1.id), str(content))

        # `GET` by `spsu`
        self.client.login(username='spsu', password='spsu')
        response = self.client.get('/procedures/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 4)
        self.assertIn(str(ksspsu_proc_1.id), str(content))

    def test_procedure_complete(self):
        """
        Assert that a `Host` can `complete` a procedure.
        """
        # Create `Events`

        # KSSPSU
        self.client.login(username='ksspsu', password='ksspsu')

        response = self.client.post('/events/', self.data)
        ksspsu_event = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Procedures`
        event = Event.objects.get(id=ksspsu_event['id'])
        ksspsu_proc_1 = Procedure.objects.create(event=event,
                                                 description='Interior Sweep')

        response = self.client.post('/procedures/' + str(ksspsu_proc_1.id) + '/complete/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/procedures/')
        content = json.loads(response.content)['results']
        self.assertIsNotNone(content[0]['completion_time'])

    """
                             INVITEE
    """

    def test_invitee_hosts_and_admins_only_dangerous_requests(self):
        """
        Assert that only `Host`s and `is_superuser`s are allowed to do non
        safe requests.
        """
        self.client.login(username='ksspsu', password='ksspsu')

        # Create `Event`
        response = self.client.post('/events/', self.data)
        event_one = json.loads(response.content)

        # `Host` create `Invitee`
        response = self.client.post('/invitees/',
                                    {'first_name': 'Josh',
                                     'last_name': 'Eppinette',
                                     'gender': 'Male',
                                     'event': event_one['id']})
        proc = json.loads(response.content)

        # Test `Nationals` cannot `POST`
        self.client.login(username='ks', password='ks')
        response = self.client.get('/invitees/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 1)

        response = self.client.post('/invitees/',
                                    {'first_name': 'John',
                                     'last_name': 'Bob',
                                     'gender': 'Male',
                                     'event': event_one['id']})
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test `Nationals` cannot `DELETE`
        response = self.client.delete('/invitees/' + str(proc['id']) + '/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test `Administrator` cannot `POST`
        self.client.login(username='spsu', password='spsu')
        response = self.client.get('/invitees/')
        content = json.loads(response.content)['results']
        self.assertEquals(len(content), 1)

        response = self.client.post('/invitees/',
                                    {'first_name': 'John',
                                     'last_name': 'Bob',
                                     'gender': 'Male',
                                     'event': event_one['id']})
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test `Administrator` cannot `DELETE`
        response = self.client.delete('/invitees/' + str(proc['id']) + '/')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

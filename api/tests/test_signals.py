"""
Asserts that the Water Dragon Signals are working properly.

The following tests can be executed with the following command.
    
    `coverage run --source='api' manage.py test api`

    This command will run all tests files in `api/tests/` and will generate a
    coverage report that can be seen by running `coverage -rm`.

Note:

    All testing commands need to executed from the directory containing
    `manage.py`.
"""

from django.test import TestCase
from django.test.utils import override_settings

# Custom User Model
from django.contrib.auth import get_user_model

# User Helper Models
from api.models import Organization, University

# User Profile Models
from api.models import Nationals, Administrator, Host

# Email Helper Models
from api.models import CarbonCopyAddress

# Event Models
from api.models import Event

def create_user(username, password):
    """
    Create a user given an username and password.
    """
    return get_user_model().objects.create_user(username=username,
                                                email=username+'@'+username+'.com',
                                                password=password)


class SignalsTests(TestCase):
    """
    The following tests have been created to assert that the api's 
    Signals are working properly.
    """

    def test_new_nationals_notification(self):
        """
        Assert that when a new `Nationals` is created, a notification is sent
        to the admins.
        """
        josh = create_user('josh', 'josh')
        josh.is_superuser = True
        josh.save()

        ks = Organization.objects.create(name='Kappa Sigma')
        kappa_sigma_nat_user = create_user('ks', 'ks')
        Nationals.objects.create(user=kappa_sigma_nat_user, organization=ks)

    def test_new_administrator_notification(self):
        """
        Assert that when a new `Administrator` is created, a notification is sent
        to the admins.
        """
        josh = create_user('josh', 'josh')
        josh.is_superuser = True
        josh.save()

        spsu = University.objects.create(name='Southern Polytechnic State University',
                                         acronym='SPSU')
        spsu_admin_user = create_user('spsu', 'spsu')
        Administrator.objects.create(user=spsu_admin_user, university=spsu)

    def test_new_host_notification(self):
        """
        Assert that when a new `Host` is created a notification is sent to the
        admins.
        """
        josh = create_user('josh', 'josh')
        josh.is_superuser = True
        josh.save()

        ks = Organization.objects.create(name='Kappa Sigma')
        spsu = University.objects.create(name='Southern Polytechnic State University',
                                         acronym='SPSU')

        ksspsu_host_user = create_user('ksspsu', 'ksspsu')
        Host.objects.create(user=ksspsu_host_user,
                            organization=ks,
                            university=spsu)

    def test_new_event_notification(self):
        """
        Assert that when a new `Event` is created a notification is sent to the
        correct administrators and `CarbonCopyAddresses`.
        """
        josh = create_user('josh', 'josh')
        josh.is_superuser = True
        josh.save()

        ks = Organization.objects.create(name='Kappa Sigma')
        spsu = University.objects.create(name='Southern Polytechnic State University',
                                         acronym='SPSU')

        ksspsu_host_user = create_user('ksspsu', 'ksspsu')
        ksspsu = Host.objects.create(user=ksspsu_host_user,
                                     organization=ks,
                                     university=spsu,
                                     enabled=True)

        spsu_admin_user = create_user('spsu', 'spsu')

        # Create `CarbonCopyAddresses` that the new event notification will also be sent to
        CarbonCopyAddress.objects.create(user=spsu_admin_user,
                                           email='bob@bob.com')
        CarbonCopyAddress.objects.create(user=spsu_admin_user,
                                           email='joe@joe.com')

        spsu_admin = Administrator.objects.create(user=spsu_admin_user,
                                                  university=spsu)
        spsu_admin.enabled = True
        spsu_admin.save()

        data = {
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

        event = Event.objects.create(host=ksspsu,
                                     **data)
                                     
        self.assertEquals(event.name, 'New Event')

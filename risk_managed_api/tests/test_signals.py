from django.contrib.auth import get_user_model
from django.test import TestCase

from risk_managed_api.models import (
    Administrator,
    CarbonCopyAddress,
    Event,
    Host,
    Nationals,
    Organization,
    University,
)


def create_user(username, password):
    return get_user_model().objects.create_user(
        username=username, email=username + "@" + username + ".com", password=password
    )


class SignalsTests(TestCase):
    def test_new_nationals_notification(self):
        josh = create_user("josh", "josh")
        josh.is_superuser = True
        josh.save()

        ks = Organization.objects.create(name="Kappa Sigma")
        kappa_sigma_nat_user = create_user("ks", "ks")
        Nationals.objects.create(user=kappa_sigma_nat_user, organization=ks)

    def test_new_administrator_notification(self):
        josh = create_user("josh", "josh")
        josh.is_superuser = True
        josh.save()

        spsu = University.objects.create(
            name="Southern Polytechnic State University", acronym="SPSU"
        )
        spsu_admin_user = create_user("spsu", "spsu")
        Administrator.objects.create(user=spsu_admin_user, university=spsu)

    def test_new_host_notification(self):
        josh = create_user("josh", "josh")
        josh.is_superuser = True
        josh.save()

        ks = Organization.objects.create(name="Kappa Sigma")
        spsu = University.objects.create(
            name="Southern Polytechnic State University", acronym="SPSU"
        )

        ksspsu_host_user = create_user("ksspsu", "ksspsu")
        Host.objects.create(user=ksspsu_host_user, organization=ks, university=spsu)

    def test_new_event_notification(self):
        josh = create_user("josh", "josh")
        josh.is_superuser = True
        josh.save()

        ks = Organization.objects.create(name="Kappa Sigma")
        spsu = University.objects.create(
            name="Southern Polytechnic State University", acronym="SPSU"
        )

        ksspsu_host_user = create_user("ksspsu", "ksspsu")
        ksspsu = Host.objects.create(
            user=ksspsu_host_user, organization=ks, university=spsu, enabled=True
        )

        spsu_admin_user = create_user("spsu", "spsu")

        # Create `CarbonCopyAddresses` that the new event notification will also be sent to
        CarbonCopyAddress.objects.create(user=spsu_admin_user, email="bob@bob.com")
        CarbonCopyAddress.objects.create(user=spsu_admin_user, email="joe@joe.com")

        spsu_admin = Administrator.objects.create(user=spsu_admin_user, university=spsu)
        spsu_admin.enabled = True
        spsu_admin.save()

        data = {
            "name": "New Event",
            "description": "My event.",
            "date": "2014-07-21",
            "time": "00:00:00.000000",
            "location": "Chapter House",
            "planner_name": "Joshua Taylor Eppinette",
            "planner_mobile": "7704016678",
            "planner_email": "josh.eppinette@waterdragon.net",
            "president_email": "pres@pres.com",
            "sober_monitors": "Josh Eppinette",
            "expected_guest_count": 50,
            "exclusivity": "Invitation Only",
            "alcohol_distribution": "Mobile Cocktails",
            "entry": "Yes",
            "entry_description": "Front Door",
            "co_sponsored_description": "With Kappa Delta",
        }

        event = Event.objects.create(host=ksspsu, **data)

        self.assertEquals(event.name, "New Event")

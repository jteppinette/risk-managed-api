import os.path
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.db import IntegrityError
from django.test import TestCase

from risk_managed_api.models import (
    Administrator,
    CarbonCopyAddress,
    Event,
    GuestRegistration,
    Host,
    Identity,
    Invitee,
    Nationals,
    Organization,
    University,
)


def create_user(username, password):
    return get_user_model().objects.create_user(
        username=username, email=username + "@" + username + ".com", password=password
    )


class ModelTests(TestCase):
    def test_user_profiles_cascade_delete(self):
        kappa_sigma = Organization.objects.create(name="Kappa Sigma")
        spsu = University.objects.create(name="Southern Poly", acronym="SPSU")

        # Nationals
        user = create_user("ks", "ks")
        ks_nat = Nationals.objects.create(user=user, organization=kappa_sigma)

        ks_nat.delete()
        users = get_user_model().objects.filter(username="ks")
        self.assertEquals(len(users), 0)

        # Administrator
        user = create_user("spsu", "spsu")
        spsu_adm = Administrator.objects.create(user=user, university=spsu)

        spsu_adm.delete()
        users = get_user_model().objects.filter(username="spsu")
        self.assertEquals(len(users), 0)

        # Host
        user = create_user("ksspsu", "ksspsu")
        ksspsu_hst = Host.objects.create(user=user, university=spsu, organization=kappa_sigma)
        ksspsu_hst.delete()
        users = get_user_model().objects.filter(username="ksspsu")
        self.assertEquals(len(users), 0)

    def test_new_nationals_or_administrator_fore_host_link(self):
        admin = create_user("josh", "josh")
        admin.is_superuser = True
        admin.save()

        # Create `Organizations`
        ks = Organization.objects.create(name="Kappa Sigma")

        sae = Organization.objects.create(name="Sigma Alpha Epsilon")

        sn = Organization.objects.create(name="Sigma Nu")

        # Create `Universities`
        spsu = University.objects.create(
            name="Southern Polytechnic State University", acronym="SPSU"
        )

        gt = University.objects.create(name="Georgia Institute of Technology", acronym="GT")

        uga = University.objects.create(name="University of Georgia", acronym="UGA")

        # Create `Hosts`
        ksspsu_user = create_user("ksspsu", "ksspsu")
        Host.objects.create(user=ksspsu_user, organization=ks, university=spsu)

        saespsu_user = create_user("saespsu", "saespsu")
        Host.objects.create(user=saespsu_user, organization=sae, university=spsu)

        ksgt_user = create_user("ksgt", "ksgt")
        Host.objects.create(user=ksgt_user, organization=ks, university=gt)

        saegt_user = create_user("saegt", "saegt")
        Host.objects.create(user=saegt_user, organization=sae, university=gt)

        # Assert `Hosts` exist
        host_set = Host.objects.filter(organization=ks)
        self.assertEquals(len(host_set), 2)

        # Assert `Hosts` do not have `Nationals`
        self.assertEquals(host_set[0].nationals, None)

        # Create `Nationals`
        ks_nat_user = create_user("ks", "ks")
        ks_nat = Nationals.objects.create(user=ks_nat_user, organization=ks)

        sae_nat_user = create_user("sae", "sae")
        Nationals.objects.create(user=sae_nat_user, organization=sae)

        # Assert `Hosts` do have `Nationals`
        host_set = Host.objects.filter(nationals=ks_nat)
        self.assertEquals(len(host_set), 2)

        # Assert `Hosts` exist
        host_set = Host.objects.filter(university=spsu)
        self.assertEquals(len(host_set), 2)

        # Assert `Hosts` do not have `Administrators`
        self.assertEquals(host_set[0].administrator, None)

        # Create `Administrators`
        spsu_admin_user = create_user("spsu", "spsu")
        spsu_admin = Administrator.objects.create(user=spsu_admin_user, university=spsu)

        gt_admin_user = create_user("gt", "gt")
        Administrator.objects.create(user=gt_admin_user, university=gt)

        # Assert `Hosts` do have `Administrator`
        host_set = Host.objects.filter(administrator=spsu_admin)
        self.assertEquals(len(host_set), 2)

        # Create new `Nationals` and `Administrator` objects
        sn_nat_user = create_user("sn", "sn")
        sn_nat = Nationals.objects.create(user=sn_nat_user, organization=sn)

        uga_admin_user = create_user("uga", "uga")
        uga_admin = Administrator.objects.create(user=uga_admin_user, university=uga)

        # Create new `Host` object
        snuga_user = create_user("snuga", "snuga")
        snuga = Host.objects.create(user=snuga_user, organization=sn, university=uga)

        # Assert `Host` is automatically assigned `Nationals` and `Administrator`
        self.assertEquals(snuga.nationals, sn_nat)
        self.assertEquals(snuga.administrator, uga_admin)

    def test_number_of_hosts(self):
        ks = Organization.objects.create(name="Kappa Sigma")
        spsu = University.objects.create(
            name="Southern Polytechnic State University", acronym="SPSU"
        )

        ks_nat_user = create_user("ks", "ks")
        ks_nat = Nationals.objects.create(user=ks_nat_user, organization=ks)

        spsu_admin_user = create_user("spsu", "spsu")
        spsu_admin = Administrator.objects.create(user=spsu_admin_user, university=spsu)

        ksspsu_user = create_user("ksspsu", "ksspsu")
        Host.objects.create(user=ksspsu_user, organization=ks, university=spsu)

        self.assertEquals(ks_nat.number_of_hosts(), 1)
        self.assertEquals(spsu_admin.number_of_hosts(), 1)

        sae = Organization.objects.create(name="Sigma Alpha Epsilon")

        kssae_user = create_user("kssae", "kssae")
        Host.objects.create(user=kssae_user, organization=sae, university=spsu)

        self.assertEquals(spsu_admin.number_of_hosts(), 2)

    def test_addresses_are_deleted_on_user_profile_deletion(self):
        kappa_sigma = Organization.objects.create(name="Kappa Sigma")
        spsu = University.objects.create(name="Southern Poly", acronym="SPSU")

        user = create_user("ksspsu", "ksspsu")
        ksspsu = Host.objects.create(user=user, university=spsu, organization=kappa_sigma)

        # Create Addresses
        CarbonCopyAddress.objects.create(user=user, email="bob@bob.com")
        CarbonCopyAddress.objects.create(user=user, email="joe@joe.com")

        all_addresses = CarbonCopyAddress.objects.all()
        self.assertEquals(len(all_addresses), 2)

        ksspsu.delete()

        all_addresses = CarbonCopyAddress.objects.all()
        self.assertEquals(len(all_addresses), 0)

    def test_addresses_are_unique_with_email_and_user(self):
        josh = create_user("josh", "josh")

        # Create `CarbonCopyAddresses`
        CarbonCopyAddress.objects.create(user=josh, email="bob@bob.com")
        with self.assertRaises(IntegrityError):
            CarbonCopyAddress.objects.create(user=josh, email="bob@bob.com")

    def test_identities_unique_together(self):

        Identity.objects.create(
            first_name="Josh", last_name="Eppinette", gender="Male", dob=date(1994, 5, 12)
        )

        with self.assertRaises(IntegrityError):
            Identity.objects.create(
                first_name="Josh", last_name="Eppinette", gender="Male", dob=date(1994, 5, 12)
            )

    def test_identities_normalize_names(self):
        Identity.objects.create(
            first_name="josh", last_name="EpPinette", gender="Male", dob=date(1994, 5, 12)
        )

        with self.assertRaises(IntegrityError):
            Identity.objects.create(
                first_name="Josh", last_name="Eppinette", gender="Male", dob=date(1994, 5, 12)
            )

    def test_identities_middle_name(self):
        Identity.objects.create(
            first_name="joshua tayloR", last_name="EpPinette", gender="Male", dob=date(1994, 5, 12)
        )

        with self.assertRaises(IntegrityError):
            Identity.objects.create(
                first_name="Joshua taylor",
                last_name="Eppinette",
                gender="Male",
                dob=date(1994, 5, 12),
            )

    def test_identities_trailing_spaces(self):
        Identity.objects.create(
            first_name="joshua   ", last_name="EpPinette", gender="Male", dob=date(1994, 5, 12)
        )

        results = Identity.objects.filter(first_name="Joshua")
        self.assertEquals(len(results), 1)

    def test_events_are_unique_with_host_name_and_date(self):
        kappa_sigma = Organization.objects.create(name="Kappa Sigma")
        spsu = University.objects.create(name="Southern Poly", acronym="SPSU")
        uga = University.objects.create(name="University of Georgia", acronym="UGA")

        user = create_user("ksspsu", "ksspsu")
        ksspsu = Host.objects.create(user=user, university=spsu, organization=kappa_sigma)

        user = create_user("ksuga", "ksuga")
        ksuga = Host.objects.create(user=user, university=uga, organization=kappa_sigma)

        # Create `Events`
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

        Event.objects.create(host=ksspsu, **data)

        edited_data = data
        edited_data["date"] = "2013-07-21"
        Event.objects.create(host=ksspsu, **edited_data)

        Event.objects.create(host=ksuga, **data)

        with self.assertRaises(IntegrityError):
            Event.objects.create(host=ksspsu, **data)

    def test_invitees_normalize_names(self):
        kappa_sigma = Organization.objects.create(name="Kappa Sigma")
        spsu = University.objects.create(name="Southern Poly", acronym="SPSU")

        user = create_user("ksspsu", "ksspsu")
        ksspsu = Host.objects.create(user=user, university=spsu, organization=kappa_sigma)

        # Create `Events`
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

        event_one = Event.objects.create(host=ksspsu, **data)

        # Test `Invitees`
        Invitee.objects.create(
            first_name="josh", last_name="EpPinette", gender="Male", event=event_one
        )

        results = Invitee.objects.filter(first_name="Josh")
        self.assertEquals(len(results), 1)

    def test_invitees_trailing_spaces(self):
        kappa_sigma = Organization.objects.create(name="Kappa Sigma")
        spsu = University.objects.create(name="Southern Poly", acronym="SPSU")

        user = create_user("ksspsu", "ksspsu")
        ksspsu = Host.objects.create(user=user, university=spsu, organization=kappa_sigma)

        # Create `Events`
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

        event_one = Event.objects.create(host=ksspsu, **data)

        # Test `Invitees`
        Invitee.objects.create(
            first_name="joshua   ", last_name="Eppinette", gender="Male", event=event_one
        )

        results = Invitee.objects.filter(first_name="Joshua")
        self.assertEquals(len(results), 1)

    def test_guest_registration_creation(self):
        kappa_sigma = Organization.objects.create(name="Kappa Sigma")
        spsu = University.objects.create(name="Southern Poly", acronym="SPSU")

        user = create_user("ksspsu", "ksspsu")
        ksspsu = Host.objects.create(user=user, university=spsu, organization=kappa_sigma)

        # Create `Events`
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

        event_one = Event.objects.create(host=ksspsu, **data)

        josh = Identity.objects.create(
            first_name="Josh", last_name="Eppinette", gender="Male", dob=date(1994, 5, 12)
        )
        with open(
            os.path.join(settings.ROOT, "tests", "fixtures", "images", "checkin.jpg"), "rb"
        ) as f:
            django_file = File(f)
            django_file.name = str(josh.id) + "-" + str(event_one.id) + "-image.jpg"
            GuestRegistration.objects.create(identity=josh, event=event_one, image=django_file)

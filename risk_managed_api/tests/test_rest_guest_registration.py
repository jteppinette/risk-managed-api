import json
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

# Event Models
# Identity Models
# Email Helper Models
# User Profile Models
# User Helper Models
from risk_managed_api.models import (
    Administrator,
    Event,
    Host,
    Identity,
    Nationals,
    Organization,
    University,
)


def create_user(username, password):
    return get_user_model().objects.create_user(
        username=username, email=username + "@" + username + ".com", password=password
    )


@override_settings(DEBUG=True)
class GuestRegistrationTests(APITestCase):
    def setUp(self):
        self.admin = create_user("josh", "josh")
        self.admin.is_superuser = True
        self.admin.save()

        self.ks = Organization.objects.create(name="Kappa Sigma")
        self.spsu = University.objects.create(
            name="Southern Polytechnic State University", acronym="SPSU"
        )

        self.sae = Organization.objects.create(name="Sigma Alpha Epsilon")
        self.gt = University.objects.create(name="Georgia Institute of Technology", acronym="GT")

        ks_nat_user = create_user("ks", "ks")
        self.ks_nat = Nationals.objects.create(user=ks_nat_user, organization=self.ks, enabled=True)

        spsu_admin_user = create_user("spsu", "spsu")
        self.spsu_admin = Administrator.objects.create(
            user=spsu_admin_user, university=self.spsu, enabled=True
        )

        sae_nat_user = create_user("sae", "sae")
        self.sae_nat = Nationals.objects.create(
            user=sae_nat_user, organization=self.sae, enabled=True
        )

        gt_admin_user = create_user("gt", "gt")
        self.gt_admin = Administrator.objects.create(
            user=gt_admin_user, university=self.gt, enabled=True
        )

        ksspsu_user = create_user("ksspsu", "ksspsu")
        self.ksspsu = Host.objects.create(
            user=ksspsu_user, organization=self.ks, university=self.spsu, enabled=True
        )

        saespsu_user = create_user("saespsu", "saespsu")
        self.saespsu = Host.objects.create(
            user=saespsu_user, organization=self.sae, university=self.spsu, enabled=True
        )

        ksgt_user = create_user("ksgt", "ksgt")
        self.ksgt = Host.objects.create(
            user=ksgt_user, organization=self.ks, university=self.gt, enabled=True
        )

        self.data = {
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

        self.ksspsu_event = Event.objects.create(host=self.ksspsu, **self.data)

        self.saespsu_event = Event.objects.create(host=self.saespsu, **self.data)

        self.ksgt_event = Event.objects.create(host=self.ksgt, **self.data)

        self.josh = Identity.objects.create(
            first_name="Josh", last_name="Eppinette", gender="Male", dob="1994-05-12"
        )
        self.olivia = Identity.objects.create(
            first_name="Olivia", last_name="Eppinette", gender="Female", dob="1998-10-02"
        )
        self.stewart = Identity.objects.create(
            first_name="Stewart", last_name="Hickey", gender="Male", dob="1993-11-06"
        )
        self.sean = Identity.objects.create(
            first_name="Sean", last_name="Johnson", gender="Male", dob="1992-08-14"
        )

        ROOT = settings.ROOT
        self.image_fp = os.path.join(ROOT, "tests", "fixtures", "images", "checkin.jpg")

    def test_only_host_can_post_guest_registration(self):
        # `Host`
        self.client.login(username="ksspsu", password="ksspsu")

        with open(self.image_fp, "rb") as image_file:
            response = self.client.post(
                "/guestregistrations/",
                {"identity": self.josh.id, "event": self.ksspsu_event.id, "image": image_file},
            )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # `Nationals`
        self.client.login(username="ks", password="ks")

        with open(self.image_fp, "rb") as image_file:
            response = self.client.post(
                "/guestregistrations/",
                {"identity": self.josh.id, "event": self.ksspsu_event.id, "image": image_file},
            )

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        # `Administrator`
        self.client.login(username="spsu", password="spsu")

        with open(self.image_fp, "rb") as image_file:
            response = self.client.post(
                "/guestregistrations/",
                {"identity": self.josh.id, "event": self.ksspsu_event.id, "image": image_file},
            )

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_updates_on_guest_registrations(self):
        self.client.login(username="ksspsu", password="ksspsu")

        with open(self.image_fp, "rb") as image_file:
            response = self.client.post(
                "/guestregistrations/",
                {"identity": self.josh.id, "event": self.ksspsu_event.id, "image": image_file},
            )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put("/guestregistrations/", {"identity": self.olivia.id})

        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch("/guestregistrations/", {"identity": self.olivia.id})

        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_guest_registrations_get_queryset(self):
        # Create `GuestRegistrations`

        # `KSSPSU`
        self.client.login(username="ksspsu", password="ksspsu")
        image_file = open(self.image_fp, "rb")
        response = self.client.post(
            "/guestregistrations/",
            {"identity": self.josh.id, "event": self.ksspsu_event.id, "image": image_file},
        )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        image_file = open(self.image_fp, "rb")
        response = self.client.post(
            "/guestregistrations/",
            {"identity": self.olivia.id, "event": self.ksspsu_event.id, "image": image_file},
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # `SAESPSU`
        self.client.login(username="saespsu", password="saespsu")

        image_file = open(self.image_fp, "rb")
        response = self.client.post(
            "/guestregistrations/",
            {"identity": self.stewart.id, "event": self.saespsu_event.id, "image": image_file},
        )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # `KSGT`
        self.client.login(username="ksgt", password="ksgt")

        image_file = open(self.image_fp, "rb")
        response = self.client.post(
            "/guestregistrations/",
            {"identity": self.sean.id, "event": self.ksgt_event.id, "image": image_file},
        )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Test `get_queryset`

        # `KSSPSU`
        self.client.login(username="ksspsu", password="ksspsu")
        response = self.client.get("/guestregistrations/", {"ordering": "date_time_taken"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # `KS`
        self.client.login(username="ks", password="ks")
        response = self.client.get("/guestregistrations/", {"ordering": "date_time_taken"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 3)

        # `SPSU`
        self.client.login(username="spsu", password="spsu")
        response = self.client.get("/guestregistrations/", {"ordering": "date_time_taken"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 3)

    def test_guest_registrations_filtering(self):
        # Create `GuestRegistrations`

        # `KSSPSU`
        self.client.login(username="ksspsu", password="ksspsu")
        image_file = open(self.image_fp, "rb")
        response = self.client.post(
            "/guestregistrations/",
            {"identity": self.josh.id, "event": self.ksspsu_event.id, "image": image_file},
        )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        image_file = open(self.image_fp, "rb")
        response = self.client.post(
            "/guestregistrations/",
            {"identity": self.olivia.id, "event": self.ksspsu_event.id, "image": image_file},
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # `SAESPSU`
        self.client.login(username="saespsu", password="saespsu")

        image_file = open(self.image_fp, "rb")
        response = self.client.post(
            "/guestregistrations/",
            {"identity": self.stewart.id, "event": self.saespsu_event.id, "image": image_file},
        )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # `KSGT`
        self.client.login(username="ksgt", password="ksgt")

        image_file = open(self.image_fp, "rb")
        response = self.client.post(
            "/guestregistrations/",
            {"identity": self.sean.id, "event": self.ksgt_event.id, "image": image_file},
        )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Test filtering

        # `KSSPSU`
        self.client.login(username="ksspsu", password="ksspsu")

        response = self.client.get(
            "/guestregistrations/", {"first_name": "Josh", "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get(
            "/guestregistrations/", {"last_name": "Eppinette", "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        response = self.client.get(
            "/guestregistrations/", {"gender": "Female", "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        # `KS`
        self.client.login(username="ks", password="ks")

        response = self.client.get(
            "/guestregistrations/", {"event": self.ksspsu_event.id, "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # `SPSU`
        self.client.login(username="spsu", password="spsu")

        response = self.client.get(
            "/guestregistrations/", {"event": self.saespsu_event.id, "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get(
            "/guestregistrations/", {"identity": self.josh.id, "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get(
            "/guestregistrations/", {"event": self.ksspsu_event.id, "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # Custom Filtering
        self.client.login(username="ksspsu", password="ksspsu")

        response = self.client.get(
            "/guestregistrations/", {"search": "josh Male eppinette", "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get(
            "/guestregistrations/", {"search": "Male os", "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get(
            "/guestregistrations/", {"search": "Female", "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get(
            "/guestregistrations/", {"search": "Female ppi", "ordering": "date_time_taken"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

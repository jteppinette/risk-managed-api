import json

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from risk_managed_api.models import Administrator, Event, Host, Invitee, Nationals, Procedure


def create_user(username, password):
    return get_user_model().objects.create_user(
        username=username, email=username + "@" + username + ".com", password=password
    )


class RestFilteringTests(APITestCase):
    def test_filter_organization(self):
        admin = create_user("josh", "josh")
        admin.is_superuser = True
        admin.save()

        self.client.login(username="josh", password="josh")

        # Create `Organizations`
        self.client.post("/organizations/", {"name": "Kappa Sigma"})
        self.client.post("/organizations/", {"name": "Sigma Alpha Epsilon"})
        self.client.post("/organizations/", {"name": "Sigma Nu"})
        self.client.post("/organizations/", {"name": "Theta Xi"})
        response = self.client.post("/organizations/", {"name": "Kappa Alpha"})
        kappa_alpha = json.loads(response.content)

        # Check all objects created
        response = self.client.get("/organizations/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 5)

        # Assert icontains filtering
        response = self.client.get("/organizations/", {"name": "APP"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # Assert exact filtering
        response = self.client.get("/organizations/", {"id": str(kappa_alpha["id"])})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

    def test_filter_university(self):
        admin = create_user("josh", "josh")
        admin.is_superuser = True
        admin.save()

        self.client.login(username="josh", password="josh")

        # Create `Universities`
        self.client.post(
            "/universities/",
            {
                "name": "Southern Polytechnic State University",
                "acronym": "SPSU",
                "state": "Georgia",
            },
        )
        self.client.post(
            "/universities/",
            {"name": "Georgia Insitute of Technology", "acronym": "GT", "state": "Georgia"},
        )
        self.client.post(
            "/universities/",
            {"name": "University of Georgia", "acronym": "UGA", "state": "Georgia"},
        )
        self.client.post(
            "/universities/",
            {"name": "University of West Georgia", "acronym": "UWG", "state": "Georgia"},
        )
        self.client.post(
            "/universities/", {"name": "University of Alabama", "acronym": "UA", "state": "Alabama"}
        )
        response = self.client.post(
            "/universities/",
            {"name": "University of North Georgia", "acronym": "UNG", "state": "Georgia"},
        )

        ung = json.loads(response.content)

        # Check all objects created
        response = self.client.get("/universities/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 6)

        # Assert icontains filtering
        response = self.client.get("/universities/", {"name": "georgia"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 4)

        # Assert iexact state filtering
        response = self.client.get("/universities/", {"state": "alabama"})
        content = json.loads(response.content)["results"]
        self.assertEquals(content[0]["acronym"], "UA")

        # Assert iexact acronym filtering
        response = self.client.get("/universities/", {"acronym": "spsu"})
        content = json.loads(response.content)["results"]
        self.assertEquals(content[0]["name"], "Southern Polytechnic State University")

        # Assert exact filtering
        response = self.client.get("/universities/", {"id": str(ung["id"])})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

    def test_filter_host(self):
        admin = create_user("josh", "josh")
        admin.is_superuser = True
        admin.save()

        self.client.login(username="josh", password="josh")

        # Create `Organizations`
        response = self.client.post("/organizations/", {"name": "Kappa Sigma"})
        ks = json.loads(response.content)

        response = self.client.post("/organizations/", {"name": "Sigma Alpha Epsilon"})
        sae = json.loads(response.content)

        # Create `Universities`
        response = self.client.post(
            "/universities/",
            {
                "name": "Southern Polytechnic State University",
                "acronym": "SPSU",
                "state": "Georgia",
            },
        )
        spsu = json.loads(response.content)

        response = self.client.post(
            "/universities/",
            {"name": "Georgia Insitute of Technology", "acronym": "GT", "state": "Georgia"},
        )
        gt = json.loads(response.content)

        # Create `Administrators`
        response = self.client.post(
            "/administrators/",
            {"username": "spsu", "password": "spsu", "university": str(spsu["id"])},
        )
        spsu_admin = json.loads(response.content)

        response = self.client.post(
            "/administrators/", {"username": "gt", "password": "gt", "university": str(gt["id"])}
        )
        gt_admin = json.loads(response.content)

        # Create `Nationals`
        response = self.client.post(
            "/nationals/", {"username": "ks", "password": "ks", "organization": str(ks["id"])}
        )
        ks_nat = json.loads(response.content)

        response = self.client.post(
            "/nationals/", {"username": "sae", "password": "sae", "organization": str(sae["id"])}
        )
        sae_nat = json.loads(response.content)

        # Create `Hosts`
        response = self.client.post(
            "/hosts/",
            {
                "username": "ksspsu",
                "password": "ksspsu",
                "organization": str(ks["id"]),
                "university": str(spsu["id"]),
                "administrator": str(spsu_admin["id"]),
                "nationals": str(ks_nat["id"]),
            },
        )
        json.loads(response.content)

        response = self.client.post(
            "/hosts/",
            {
                "username": "saespsu",
                "password": "saespsu",
                "organization": str(sae["id"]),
                "university": str(spsu["id"]),
                "administrator": str(spsu_admin["id"]),
                "nationals": str(sae_nat["id"]),
            },
        )

        json.loads(response.content)

        response = self.client.post(
            "/hosts/",
            {
                "username": "ksgt",
                "password": "ksgt",
                "organization": str(ks["id"]),
                "university": str(gt["id"]),
                "administrator": str(gt_admin["id"]),
                "nationals": str(ks_nat["id"]),
            },
        )

        json.loads(response.content)

        response = self.client.post(
            "/hosts/",
            {
                "username": "saegt",
                "password": "saegt",
                "organization": str(sae["id"]),
                "university": str(gt["id"]),
                "administrator": str(gt_admin["id"]),
                "nationals": str(sae_nat["id"]),
            },
        )

        json.loads(response.content)

        self.client.login(username="ks", password="ks")

        # Assert `Hosts` exist
        response = self.client.get("/hosts/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # Assert filter `University` by `id`
        response = self.client.get("/hosts/", {"university": str(spsu["id"])})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        self.client.login(username="spsu", password="spsu")

        # Assert `Hosts` exist
        response = self.client.get("/hosts/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # Assert filter `Organization` by `id`
        response = self.client.get("/hosts/", {"organization": str(ks["id"])})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

    def test_filter_addresses(self):
        # Create `User`
        create_user("ksspsu", "ksspsu")

        # Add `CarbonCopyAddresses`
        self.client.login(username="ksspsu", password="ksspsu")

        response = self.client.post("/carboncopyaddresses/", {"email": "josheppinette@gmail.com"})
        email_one = json.loads(response.content)

        response = self.client.post("/carboncopyaddresses/", {"email": "bob@bob.com"})
        json.loads(response.content)

        # Assert `CarbonCopyAddresses` exist
        response = self.client.get("/carboncopyaddresses/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # Filter by `email`
        response = self.client.get("/carboncopyaddresses/", {"email": "bob@bob.com"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        # Filter by `id`
        response = self.client.get("/carboncopyaddresses/", {"id": str(email_one["id"])})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

    def test_filter_identities(self):
        admin = create_user("josh", "josh")
        admin.is_superuser = True
        admin.save()

        self.client.login(username="josh", password="josh")

        # Create `Organizations`
        response = self.client.post("/organizations/", {"name": "Kappa Sigma"})
        ks = json.loads(response.content)

        response = self.client.post("/organizations/", {"name": "Sigma Alpha Epsilon"})
        json.loads(response.content)

        # Create `Universities`
        response = self.client.post(
            "/universities/",
            {
                "name": "Southern Polytechnic State University",
                "acronym": "SPSU",
                "state": "Georgia",
            },
        )
        spsu = json.loads(response.content)

        response = self.client.post(
            "/universities/",
            {"name": "Georgia Insitute of Technology", "acronym": "GT", "state": "Georgia"},
        )
        json.loads(response.content)

        # Create `Hosts`
        response = self.client.post(
            "/hosts/",
            {
                "username": "ksspsu",
                "password": "ksspsu",
                "organization": str(ks["id"]),
                "university": str(spsu["id"]),
            },
        )
        ksspsu = json.loads(response.content)

        # Enable the `Host`
        Host.objects.filter(id=ksspsu["id"]).update(enabled=True)

        # Create `Identities`
        self.client.login(username="ksspsu", password="ksspsu")

        response = self.client.post(
            "/identities/",
            {"first_name": "Josh", "last_name": "Eppinette", "gender": "Male", "dob": "1994-05-12"},
        )
        json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            "/identities/",
            {
                "first_name": "Olivia",
                "last_name": "Eppinette",
                "gender": "Female",
                "dob": "1998-10-02",
            },
        )
        json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Test basic filtering
        response = self.client.get("/identities/", {"first_name": "os"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/identities/", {"last_name": "PP"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        response = self.client.get("/identities/", {"dob": "1994-05-12"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/identities/", {"gender": "Male"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/identities/", {"dob": "1994-05-12"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        # Test custom filtering
        response = self.client.get("/identities/", {"search": "os"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/identities/", {"search": "PP Male"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)
        self.assertIn("Josh", str(content))

        response = self.client.get("/identities/", {"search": "PP Female"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)
        self.assertIn("Olivia", str(content))

        response = self.client.get("/identities/", {"search": "josh eppinette Male"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/identities/", {"search": "epp Male jo"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

    def test_filter_flags(self):
        admin = create_user("josh", "josh")
        admin.is_superuser = True
        admin.save()

        self.client.login(username="josh", password="josh")

        # Create `Organizations`
        response = self.client.post("/organizations/", {"name": "Kappa Sigma"})
        ks = json.loads(response.content)

        response = self.client.post("/organizations/", {"name": "Sigma Alpha Epsilon"})
        json.loads(response.content)

        # Create `Universities`
        response = self.client.post(
            "/universities/",
            {
                "name": "Southern Polytechnic State University",
                "acronym": "SPSU",
                "state": "Georgia",
            },
        )
        spsu = json.loads(response.content)

        response = self.client.post(
            "/universities/",
            {"name": "Georgia Insitute of Technology", "acronym": "GT", "state": "Georgia"},
        )
        json.loads(response.content)

        # Create `Hosts`
        response = self.client.post(
            "/hosts/",
            {
                "username": "ksspsu",
                "password": "ksspsu",
                "organization": str(ks["id"]),
                "university": str(spsu["id"]),
            },
        )
        ksspsu = json.loads(response.content)

        # Create `Nationals`
        response = self.client.post(
            "/nationals/", {"username": "ks", "password": "ks", "organization": str(ks["id"])}
        )
        ks_nat = json.loads(response.content)

        # Create `Administrator`
        response = self.client.post(
            "/administrators/",
            {"username": "spsu", "password": "spsu", "university": str(spsu["id"])},
        )
        spsu_admin = json.loads(response.content)

        # Enable the user profiles
        Host.objects.filter(id=ksspsu["id"]).update(enabled=True)
        Nationals.objects.all().update(enabled=True)
        Administrator.objects.all().update(enabled=True)

        # Create `Identities`
        self.client.login(username="ksspsu", password="ksspsu")

        response = self.client.post(
            "/identities/",
            {"first_name": "Josh", "last_name": "Eppinette", "gender": "Male", "dob": "1994-05-12"},
        )
        josh = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            "/identities/",
            {
                "first_name": "Olivia",
                "last_name": "Eppinette",
                "gender": "Female",
                "dob": "1998-10-02",
            },
        )
        olivia = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            "/identities/",
            {"first_name": "Bobby", "last_name": "Brown", "gender": "Male", "dob": "1993-10-02"},
        )
        bobby = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            "/identities/",
            {"first_name": "joe", "last_name": "brooks", "gender": "Male", "dob": "1991-10-02"},
        )
        joe = json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Create `Flags`
        self.client.login(username="ksspsu", password="ksspsu")

        response = self.client.post("/flags/", {"identity": josh["id"], "violation": "Stealing"})
        json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            "/flags/", {"identity": olivia["id"], "violation": "Underage Drinking"}
        )
        json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self.client.login(username="ks", password="ks")

        response = self.client.post("/flags/", {"identity": bobby["id"], "violation": "Stealing"})
        json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self.client.login(username="spsu", password="spsu")

        response = self.client.post("/flags/", {"identity": joe["id"], "violation": "Stealing"})
        json.loads(response.content)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Filter `Flags`
        self.client.login(username="ksspsu", password="ksspsu")
        response = self.client.get("/flags/", {"first_name": "josh"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/flags/", {"gender": "Female"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/flags/", {"last_name": "epp"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        response = self.client.get("/flags/", {"dob": "1994-05-12"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/flags/", {"nationals": ks_nat["id"]})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/flags/", {"administrator": spsu_admin["id"]})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/flags/", {"host": ksspsu["id"]})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # Complex Filtering

        response = self.client.get("/flags/", {"search": "Male josh pp"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/flags/", {"search": "pp Male"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/flags/", {"search": "Female olivia"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/flags/", {"search": "Female"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get(
            "/flags/", {"search": "Male joe oo", "administrator": spsu_admin["id"]}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

    def test_filter_events(self):
        admin = create_user("josh", "josh")
        admin.is_superuser = True
        admin.save()

        self.client.login(username="josh", password="josh")

        # Create `Organizations`
        response = self.client.post("/organizations/", {"name": "Kappa Sigma"})
        ks = json.loads(response.content)

        response = self.client.post("/organizations/", {"name": "Sigma Alpha Epsilon"})
        json.loads(response.content)

        # Create `Universities`
        response = self.client.post(
            "/universities/",
            {
                "name": "Southern Polytechnic State University",
                "acronym": "SPSU",
                "state": "Georgia",
            },
        )
        spsu = json.loads(response.content)

        response = self.client.post(
            "/universities/",
            {"name": "Georgia Insitute of Technology", "acronym": "GT", "state": "Georgia"},
        )
        json.loads(response.content)

        # Create `Hosts`
        response = self.client.post(
            "/hosts/",
            {
                "username": "ksspsu",
                "password": "ksspsu",
                "organization": str(ks["id"]),
                "university": str(spsu["id"]),
            },
        )
        ksspsu = json.loads(response.content)

        # Enable the `Host`
        Host.objects.filter(id=ksspsu["id"]).update(enabled=True)

        # `Event` default data
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

        # Create `Events`
        self.client.login(username="ksspsu", password="ksspsu")
        response = self.client.post("/events/", data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        event_one = json.loads(response.content)

        data["name"] = "New Event 2"
        response = self.client.post("/events/", data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        # Test `Filter`
        self.client.login(username="ks", password="ks")
        response = self.client.get("/events/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        response = self.client.get("/events/", {"name": "2"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get("/events/", {"id": event_one["id"]})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

    def test_filter_procedures(self):
        admin = create_user("josh", "josh")
        admin.is_superuser = True
        admin.save()

        self.client.login(username="josh", password="josh")

        # Create `Organizations`
        response = self.client.post("/organizations/", {"name": "Kappa Sigma"})
        ks = json.loads(response.content)

        response = self.client.post("/organizations/", {"name": "Sigma Alpha Epsilon"})
        sae = json.loads(response.content)

        # Create `Universities`
        response = self.client.post(
            "/universities/",
            {
                "name": "Southern Polytechnic State University",
                "acronym": "SPSU",
                "state": "Georgia",
            },
        )
        spsu = json.loads(response.content)

        response = self.client.post(
            "/universities/",
            {"name": "Georgia Insitute of Technology", "acronym": "GT", "state": "Georgia"},
        )
        gt = json.loads(response.content)

        # Create `Nationals`
        response = self.client.post(
            "/nationals/", {"username": "ks", "password": "ks", "organization": str(ks["id"])}
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        response = self.client.post(
            "/nationals/", {"username": "sae", "password": "sae", "organization": str(sae["id"])}
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        # Create `Administrators`
        response = self.client.post(
            "/administrators/",
            {"username": "spsu", "password": "spsu", "university": str(spsu["id"])},
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        response = self.client.post(
            "/administrators/", {"username": "gt", "password": "gt", "university": str(gt["id"])}
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        # Create `Hosts`
        response = self.client.post(
            "/hosts/",
            {
                "username": "ksspsu",
                "password": "ksspsu",
                "organization": str(ks["id"]),
                "university": str(spsu["id"]),
            },
        )
        ksspsu = json.loads(response.content)

        response = self.client.post(
            "/hosts/",
            {
                "username": "saespsu",
                "password": "saespsu",
                "organization": str(sae["id"]),
                "university": str(spsu["id"]),
            },
        )
        saespsu = json.loads(response.content)

        response = self.client.post(
            "/hosts/",
            {
                "username": "ksgt",
                "password": "ksgt",
                "organization": str(ks["id"]),
                "university": str(gt["id"]),
            },
        )
        ksgt = json.loads(response.content)

        # Enable the `Nationals`, `Administrators`, `Hosts`
        Nationals.objects.all().update(enabled=True)
        Administrator.objects.all().update(enabled=True)
        Host.objects.all().update(enabled=True)

        # `Event` default data
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

        # Create `Events`

        # KSSPSU
        self.client.login(username="ksspsu", password="ksspsu")
        response = self.client.post("/events/", data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        ksspsu_event = json.loads(response.content)

        # SAESPSU
        self.client.login(username="saespsu", password="saespsu")
        response = self.client.post("/events/", data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        # KSGT
        self.client.login(username="ksgt", password="ksgt")
        response = self.client.post("/events/", data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        # Test `Events`

        # `Nationals`
        self.client.login(username="ks", password="ks")

        response = self.client.get("/events/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # `Administrator`
        self.client.login(username="gt", password="gt")

        response = self.client.get("/events/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        # `Host`
        self.client.login(username="ksspsu", password="ksspsu")

        response = self.client.get("/events/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        # Create `Procedures`
        event = Event.objects.get(host__id=ksspsu["id"])
        Procedure.objects.create(description="Interior Sweep", event=event)

        event = Event.objects.get(host__id=saespsu["id"])
        Procedure.objects.create(description="Interior Sweep", event=event)

        event = Event.objects.get(host__id=ksgt["id"])
        Procedure.objects.create(description="Interior Sweep", event=event)

        # Test `Procedure` filtering

        # `Nationals`
        self.client.login(username="ks", password="ks")
        response = self.client.get("/procedures/", {"host": ksspsu["id"]})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        # `Administrator`
        self.client.login(username="spsu", password="spsu")
        response = self.client.get("/procedures/", {"host": ksspsu["id"]})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        # `Host`
        self.client.login(username="ksspsu", password="ksspsu")
        response = self.client.get("/procedures/", {"event": 10})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 0)

        self.client.login(username="ksspsu", password="ksspsu")
        response = self.client.get("/procedures/", {"event": ksspsu_event["id"]})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

    def test_filter_invitees(self):
        admin = create_user("josh", "josh")
        admin.is_superuser = True
        admin.save()

        self.client.login(username="josh", password="josh")

        # Create `Organizations`
        response = self.client.post("/organizations/", {"name": "Kappa Sigma"})
        ks = json.loads(response.content)

        response = self.client.post("/organizations/", {"name": "Sigma Alpha Epsilon"})
        sae = json.loads(response.content)

        # Create `Universities`
        response = self.client.post(
            "/universities/",
            {
                "name": "Southern Polytechnic State University",
                "acronym": "SPSU",
                "state": "Georgia",
            },
        )
        spsu = json.loads(response.content)

        response = self.client.post(
            "/universities/",
            {"name": "Georgia Insitute of Technology", "acronym": "GT", "state": "Georgia"},
        )
        gt = json.loads(response.content)

        # Create `Nationals`
        response = self.client.post(
            "/nationals/", {"username": "ks", "password": "ks", "organization": str(ks["id"])}
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        response = self.client.post(
            "/nationals/", {"username": "sae", "password": "sae", "organization": str(sae["id"])}
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        # Create `Administrators`
        response = self.client.post(
            "/administrators/",
            {"username": "spsu", "password": "spsu", "university": str(spsu["id"])},
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        response = self.client.post(
            "/administrators/", {"username": "gt", "password": "gt", "university": str(gt["id"])}
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        # Create `Hosts`
        response = self.client.post(
            "/hosts/",
            {
                "username": "ksspsu",
                "password": "ksspsu",
                "organization": str(ks["id"]),
                "university": str(spsu["id"]),
            },
        )
        ksspsu = json.loads(response.content)

        response = self.client.post(
            "/hosts/",
            {
                "username": "saespsu",
                "password": "saespsu",
                "organization": str(sae["id"]),
                "university": str(spsu["id"]),
            },
        )
        saespsu = json.loads(response.content)

        response = self.client.post(
            "/hosts/",
            {
                "username": "ksgt",
                "password": "ksgt",
                "organization": str(ks["id"]),
                "university": str(gt["id"]),
            },
        )
        ksgt = json.loads(response.content)

        # Enable the `Nationals`, `Administrators`, `Hosts`
        Nationals.objects.all().update(enabled=True)
        Administrator.objects.all().update(enabled=True)
        Host.objects.all().update(enabled=True)

        # `Event` default data
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

        # Create `Events`

        # KSSPSU
        self.client.login(username="ksspsu", password="ksspsu")
        response = self.client.post("/events/", data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        ksspsu_event = json.loads(response.content)

        # SAESPSU
        self.client.login(username="saespsu", password="saespsu")
        response = self.client.post("/events/", data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        # KSGT
        self.client.login(username="ksgt", password="ksgt")
        response = self.client.post("/events/", data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        json.loads(response.content)

        # Test `Events`

        # `Nationals`
        self.client.login(username="ks", password="ks")

        response = self.client.get("/events/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # `Administrator`
        self.client.login(username="gt", password="gt")

        response = self.client.get("/events/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        # `Host`
        self.client.login(username="ksspsu", password="ksspsu")

        response = self.client.get("/events/")
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        # Create `Procedures`
        event = Event.objects.get(host__id=ksspsu["id"])
        Invitee.objects.create(first_name="Josh", last_name="Eppinette", gender="Male", event=event)

        Invitee.objects.create(first_name="Bobby", last_name="Brown", gender="Male", event=event)

        Invitee.objects.create(
            first_name="Olivia", last_name="Eppinette", gender="Female", event=event
        )

        event = Event.objects.get(host__id=saespsu["id"])
        Invitee.objects.create(first_name="Josh", last_name="Smith", gender="Male", event=event)

        event = Event.objects.get(host__id=ksgt["id"])
        Invitee.objects.create(first_name="Josh", last_name="Brown", gender="Male", event=event)

        # Test `Invitee` basic filtering

        # `Nationals`
        self.client.login(username="ks", password="ks")
        response = self.client.get("/invitees/", {"host": ksspsu["id"]})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 3)
        self.assertIn("Eppinette", str(content))

        # `Administrator`
        self.client.login(username="spsu", password="spsu")
        response = self.client.get("/invitees/", {"host": ksspsu["id"]})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 3)
        self.assertIn("Eppinette", str(content))

        # `Host`
        self.client.login(username="ksspsu", password="ksspsu")
        response = self.client.get("/invitees/", {"event": 10})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 0)

        self.client.login(username="ksspsu", password="ksspsu")
        response = self.client.get("/invitees/", {"event": ksspsu_event["id"]})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 3)
        self.assertIn("Eppinette", str(content))

        # `Invitee` complex filtering
        # `Host`
        self.client.login(username="ksspsu", password="ksspsu")
        response = self.client.get(
            "/invitees/", {"event": ksspsu_event["id"], "first_name": "Josh"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get(
            "/invitees/", {"event": ksspsu_event["id"], "last_name": "eppinette"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        response = self.client.get("/invitees/", {"event": ksspsu_event["id"], "gender": "Male"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        # Test `name` custom filter

        response = self.client.get("/invitees/", {"event": ksspsu_event["id"], "name": "epp"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 2)

        response = self.client.get("/invitees/", {"event": ksspsu_event["id"], "name": "josh"})
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

        response = self.client.get(
            "/invitees/", {"event": ksspsu_event["id"], "name": "eppinette j"}
        )
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)

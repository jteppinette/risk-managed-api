import json

from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase


def create_user(username, password):
    return get_user_model().objects.create_user(
        username=username, email=username + "@" + username + ".com", password=password
    )


class UserHelpersRestTests(APITestCase):
    def test_admin_or_read_only(self):
        admin_user = create_user("josh", "test")
        admin_user.is_superuser = True
        admin_user.save()

        user = create_user("ks", "ks")

        self.client.login(username="josh", password="test")

        # Initial `Organizations` by admin
        response = self.client.post("/organizations/", {"name": "Kappa Sigma"})
        response = self.client.post("/organizations/", {"name": "Sigma Alpha Epsilon"})
        # Initial `Universities` by admin
        response = self.client.post(
            "/universities/",
            {
                "name": "Southern Polytechnic State University",
                "acronym": "SPSU",
                "state": "Georgia",
            },
        )

        self.client.login(username="ks", password="ks")

        # Organization by non admin `User`
        response = self.client.post("/organizations/", {"name": "Sigma Nu"})
        # University by non admin `User`
        response = self.client.post(
            "/organizations/",
            {"name": "Georgia Institute of Technology", "acronym": "GT", "state": "Georgia"},
        )

        # Test for correct number of `Organizations`
        response = self.client.get("/organizations/")
        content = json.loads(response.content)["results"]

        self.assertEquals(len(content), 2)
        self.assertIn("Kappa Sigma", str(content))

        # Test for correct number of `Universities`
        response = self.client.get("/universities/")
        content = json.loads(response.content)["results"]

        self.assertEquals(len(content), 1)
        self.assertIn("Southern", str(content))

        # Clean up models
        admin_user.delete()
        user.delete()

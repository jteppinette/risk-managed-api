import copy
import itertools
import os
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from risk_managed_api import models
from risk_managed_api.management.commands import fixtures


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-f", "--force", action="store_true", dest="force", default=False, help="Force DB Wipe"
        )

    def handle(self, *args, **kwargs):
        if not kwargs.get("force"):
            choice = input()
            if choice != "DELETE":
                return

        random.seed(1)

        User = get_user_model()

        models.Organization.objects.all().delete()
        models.University.objects.all().delete()
        models.Nationals.objects.all().delete()
        models.Administrator.objects.all().delete()
        models.Host.objects.all().delete()
        models.CarbonCopyAddress.objects.all().delete()
        models.Identity.objects.all().delete()
        models.Flag.objects.all().delete()
        models.Event.objects.all().delete()
        models.Procedure.objects.all().delete()
        models.Invitee.objects.all().delete()
        models.GuestRegistration.objects.all().delete()
        User.objects.all().exclude(is_superuser=True).delete()

        def build_create_user_kwargs(record):
            username = "{first_initial}{last_name}".format(
                first_initial=record["first_name"][0], last_name=record["last_name"]
            ).lower()
            kwargs = copy.deepcopy(record)
            kwargs["username"] = username
            kwargs["password"] = username
            return kwargs

        users = [
            User.objects.create_user(**build_create_user_kwargs(record))
            for record in fixtures.USER_RECORDS
        ]
        print("USERS: COUNT={}".format(len(users)))

        carbon_copy_addresses = models.CarbonCopyAddress.objects.bulk_create(
            itertools.chain.from_iterable(
                [
                    [
                        models.CarbonCopyAddress(email=cc_user.email, user=user)
                        for cc_user in random.sample(users, random.randint(0, 5))
                    ]
                    for user in users
                ]
            )
        )
        print("CARBON_COPY_ADDRESSES: COUNT={}".format(len(carbon_copy_addresses)))

        organizations = models.Organization.objects.bulk_create(
            [models.Organization(name=name) for name in fixtures.ORGANIZATION_NAMES]
        )
        print("ORGANIZATIONS: COUNT={}".format(len(organizations)))
        universities = models.University.objects.bulk_create(
            [models.University(**record) for record in fixtures.UNIVERSITY_RECORDS]
        )
        print("UNIVERSITIES: COUNT={}".format(len(universities)))

        admins = users[
            : len(organizations) + len(universities) + (len(organizations) * len(universities))
        ]

        nationals = models.Nationals.objects.bulk_create(
            [
                models.Nationals(user=admins.pop(), organization=organization, enabled=True)
                for organization in organizations
            ]
        )
        print("NATIONALS: COUNT={}".format(len(nationals)))

        administrators = models.Administrator.objects.bulk_create(
            [
                models.Administrator(user=admins.pop(), university=university, enabled=True)
                for university in universities
            ]
        )
        print("ADMINISTRATORS: COUNT={}".format(len(administrators)))

        hosts = models.Host.objects.bulk_create(
            itertools.chain.from_iterable(
                [
                    [
                        models.Host(
                            user=admins.pop(),
                            university=administrator.university,
                            organization=_nationals.organization,
                            nationals=_nationals,
                            enabled=True,
                        )
                        for administrator in administrators
                    ]
                    for _nationals in nationals
                ]
            )
        )
        print("HOSTS: COUNT={}".format(len(hosts)))

        events = models.Event.objects.bulk_create(
            [
                models.Event(
                    host=host, name=random.choice(fixtures.EVENT_NAMES), **fixtures.EVENT_RECORD
                )
                for host in hosts
            ]
        )
        print("EVENTS: COUNT={}".format(len(events)))

        procedures = models.Procedure.objects.bulk_create(
            itertools.chain.from_iterable(
                [
                    [
                        models.Procedure(event=event, description="Interior Sweep"),
                        models.Procedure(event=event, description="Exterior Sweep"),
                    ]
                    for event in events
                ]
            )
        )
        print("PROCEDURES: COUNT={}".format(len(procedures)))

        invitees = models.Invitee.objects.bulk_create(
            itertools.chain.from_iterable(
                [
                    [
                        models.Invitee(
                            event=event,
                            gender=record["gender"],
                            first_name=record["first_name"],
                            last_name=record["last_name"],
                        )
                        for record in random.sample(
                            fixtures.IDENTITY_RECORDS, random.randint(20, 500)
                        )
                    ]
                    for event in events
                ]
            )
        )
        print("INVITEES: COUNT={}".format(len(invitees)))

        identities = models.Identity.objects.bulk_create(
            [models.Identity(**record) for record in fixtures.IDENTITY_RECORDS]
        )
        print("IDENTITIES: COUNT={}".format(len(identities)))

        nationals_flags = models.Flag.objects.bulk_create(
            itertools.chain.from_iterable(
                [
                    [
                        models.Flag(
                            identity=random.choice(identities),
                            nationals=_nationals,
                            reach="Nationals",
                            violation=random.choice(models.Flag.VIOLATIONS)[0],
                        )
                        for _ in range(random.randint(0, 50))
                    ]
                    for _nationals in nationals
                ]
            )
        )
        print("NATIONALS_FLAGS: COUNT={}".format(len(nationals_flags)))

        administrator_flags = models.Flag.objects.bulk_create(
            itertools.chain.from_iterable(
                [
                    [
                        models.Flag(
                            identity=random.choice(identities),
                            administrator=administrator,
                            reach="Administrator",
                            violation=random.choice(models.Flag.VIOLATIONS)[0],
                        )
                        for _ in range(random.randint(0, 50))
                    ]
                    for administrator in administrators
                ]
            )
        )
        print("ADMINISTRATOR_FLAGS: COUNT={}".format(len(administrator_flags)))

        host_flags = models.Flag.objects.bulk_create(
            itertools.chain.from_iterable(
                [
                    [
                        models.Flag(
                            identity=random.choice(identities),
                            host=host,
                            reach="Host",
                            violation=random.choice(models.Flag.VIOLATIONS)[0],
                        )
                        for _ in range(random.randint(0, 50))
                    ]
                    for host in hosts
                ]
            )
        )
        print("HOST_FLAGS: COUNT={}".format(len(host_flags)))

        checkin_image = File(
            open(os.path.join(settings.ROOT, "tests", "fixtures", "images", "checkin.jpg"), "rb")
        )

        for event in events:
            event_invitees = list(event.invitees.all())
            event_registrations = []

            for invitee in random.sample(event_invitees, random.randint(0, len(event_invitees))):
                identity = models.Identity.objects.filter(
                    first_name=invitee.first_name,
                    last_name=invitee.last_name,
                    gender=invitee.gender,
                ).first()
                checkin_image.name = "{identity_id}-{event_id}-image.jpg".format(
                    identity_id=identity.id, event_id=event.id
                )
                event_registrations.append(
                    models.GuestRegistration.objects.create(
                        identity=identity, event=event, image=File(checkin_image)
                    )
                )

            print(
                'EVENT_REGISTRATIONS: HOST="{}" EVENT="{}" COUNT={}'.format(
                    event.host, event.name, len(event_registrations)
                )
            )

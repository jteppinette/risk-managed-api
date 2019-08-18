from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.renderers import JSONRenderer

from risk_managed_api.models import Administrator, Host, Nationals
from risk_managed_api.serializers import EventSerializer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def welcome_user(sender, **kwargs):
    if kwargs["created"] is False:
        return

    user = kwargs["instance"]
    send_mail(
        "Welcome to Risk Managed API", "", settings.EMAIL_FROM, [user.email], fail_silently=False
    )


def administrative_notification(content=""):
    # Build `to` list
    users = get_user_model().objects.filter(is_superuser=True).values("email")
    to_list = []

    for user in users:
        to_list.append(str(user["email"]))

    send_mail(
        "Administrative Notification", content, settings.EMAIL_FROM, to_list, fail_silently=False
    )


@receiver(post_save, sender=Nationals)
def administrative_notification_new_nationals(sender, **kwargs):
    if kwargs["created"] is False:
        return

    organization = kwargs["instance"].organization
    email = kwargs["instance"].user.email

    content = (
        "A new " + str(organization) + " Nationals has been created."
        "\nYou can contact them at " + str(email) + " ."
    )

    administrative_notification(content)


@receiver(post_save, sender=Administrator)
def administrative_notification_new_administrator(sender, **kwargs):
    if kwargs["created"] is False:
        return

    university = kwargs["instance"].university
    email = kwargs["instance"].user.email

    content = (
        "A new " + str(university) + " Administrator has been created."
        "\nYou can contact them at " + str(email) + " ."
    )

    administrative_notification(content)


@receiver(post_save, sender=Host)
def administrative_notification_new_host(sender, **kwargs):
    if kwargs["created"] is False:
        return

    # Retreive `instance` from `kwargs`
    inst = kwargs["instance"]

    organization = inst.organization
    university = inst.university
    email = inst.user.email

    content = (
        "A new " + str(organization) + " of " + str(university) + " "
        "Host has been created. You can contact them at " + str(email) + " ."
    )

    administrative_notification(content)


@receiver(post_save, sender="api.Event")
def new_event_notification(sender, **kwargs):
    if kwargs["created"] is False:
        return

    inst = kwargs["instance"]

    host = Host.objects.get(id=kwargs["instance"].host_id)
    administrator = host.administrator

    if administrator is None:
        return

    # Build `to` list
    ccs = administrator.user.addresses.values("email")
    to_list = [str(administrator.user.email)]

    for cc in ccs:
        to_list.append(str(cc["email"]))

    serializer = EventSerializer(inst)

    send_mail(
        "New Event",
        JSONRenderer().render(serializer.data),
        settings.EMAIL_FROM,
        to_list,
        fail_silently=False,
    )

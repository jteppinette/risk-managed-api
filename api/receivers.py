"""
Define the signal receivers used in the api app.
"""

from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.dispatch import receiver
from django.conf import settings

from rest_framework.renderers import JSONRenderer

# Custom User Model
from django.contrib.auth import get_user_model

# User Helper Models
from api.models import Organization, University

# User Profile Models
from api.models import Nationals, Administrator, Host

# Email Helper Models
from api.models import CarbonCopyAddress

# Event Serializer
from api.serializers import EventSerializer

"""
                             USER HELPER MODELS
"""

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def welcome_user(sender, **kwargs):
    """
    If the object is being created for the first time, send a welcome email to
    the user.
    """
    if kwargs['created'] is False:
        return 

    user = kwargs['instance']
    send_mail(
        'Welcome to Water Dragon',
        '',
        'support@waterdragon.net',
        [user.email],
        fail_silently=False,
    )

"""
                             ADMINISTRATIVE NOTIFICATION
"""

def administrative_notification(content=''):
    """
    Send a notification to all `Users` that are `is_superuser`.
    """
    # Build `to` list
    users = get_user_model().objects.filter(is_superuser=True).values('email')
    to_list = []

    for user in users:
        to_list.append({'type': 'to', 'email': str(user['email'])})

    send_mail(
        'Administrative Notification',
        content,
        'support@waterdragon.net',
        to_list,
        fail_silently=False,
    )

"""
                             USER PROFILE MODELS
"""

@receiver(post_save, sender=Nationals)
def administrative_notification_new_nationals(sender, **kwargs):
    """
    Alert all admin level `Users` that a new `Nationals` has been created.
    """
    if kwargs['created'] is False:
        return 

    organization = kwargs['instance'].organization
    email = kwargs['instance'].user.email
    
    content = ('A new ' + str(organization) + ' Nationals has been created.'
               '\nYou can contact them at ' + str(email) + ' .')

    administrative_notification(content)

@receiver(post_save, sender=Administrator)
def administrative_notification_new_administrator(sender, **kwargs):
    """
    Alert all admin level `Users` that a new `Administrator` has been created.
    """
    if kwargs['created'] is False:
        return 

    university = kwargs['instance'].university
    email = kwargs['instance'].user.email
    
    content = ('A new ' + str(university) + ' Administrator has been created.'
               '\nYou can contact them at ' + str(email) + ' .')

    administrative_notification(content)

@receiver(post_save, sender=Host)
def administrative_notification_new_host(sender, **kwargs):
    """
    Alert all admin level `Users` that a new `Host` has been created that
    does not have a `Nationals` or `Administrator`.
    """
    if kwargs['created'] is False:
        return 

    # Retreive `instance` from `kwargs`
    inst = kwargs['instance']

    # Check if `Host` has a `Nationals` or `Administrator`
    nationals = inst.nationals
    administrator = inst.administrator

    organization = inst.organization
    university = inst.university
    email = inst.user.email
    
    content = ('A new ' + str(organization) + ' of ' + str(university) + ' '
               'Host has been created. You can contact them at ' + str(email) + ' .')

    administrative_notification(content)

"""
                             EVENT MODELS
"""

@receiver(post_save, sender='api.Event')
def new_event_notification(sender, **kwargs):
    """
    Alert the `Administrator` and `CarbonCopyAddresses` of a new `Event`. 
    """
    if kwargs['created'] is False:
        return 

    inst = kwargs['instance']

    host = Host.objects.get(id=kwargs['instance'].host_id)
    administrator = host.administrator

    if administrator is None:
        return

    # Build `to` list
    ccs = administrator.user.addresses.values('email')
    to_list = [{'type': 'to', 'email': str(administrator.user.email)}]

    for cc in ccs:
        to_list.append({'type': 'cc', 'email': str(cc['email'])})

    serializer = EventSerializer(inst)

    send_mail(
        'New Event',
        JSONRenderer().render(serializer.data),
        'support@waterdragon.net',
        to_list,
        fail_silently=False,
    )


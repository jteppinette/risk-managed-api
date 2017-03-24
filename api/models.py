"""
Define all models that are associated with Water Dragon.

The Water Dragon receivers are defined at the bottom of this page.

These definitions also include the overriding of methods and other meta class
information.

The Water Dragon models are seperated into groups described below.
        
        USER HELPER MODELS:
            
            * Organization
            * University

        USER PROFILE MODELS:

            * Nationals
            * Administrator
            * Host

        EMAIL HELPER MODELS:

            * CarbonCopyAddress

        IDENTITY MODELS:
            
            * Identity
            * Flag

        EVENT MODELS:

            * Event
            * Procedure
            * Invitee

        GUEST REGISTRATION MODEL:

            * GuestRegistration
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image
from StringIO import StringIO
from io import BytesIO

from django_minio.storage import MinioStorage


"""
                             USER HELPER MODELS

    The following models are used as foreign keys from `USER MODELS`. 

        * Organization
        * University
"""


class Organization(models.Model):
    """
    The `Organization` model represents one of the many greek organizations in
    `Merica. An example of an organization is `Kappa Sigma`.
    """
    name = models.CharField(max_length=80, unique=True)

    def __unicode__(self):
        """
        Return a unicode representation of this model.
        """
        return self.name


class University(models.Model):
    """
    The `University` model represents one of the many universities in `Merica
    that have a Greek system. An example university is `Southern Polytechnic
    State University`.

    Each `University` contains a `name` and `acronym` field. This is too allow
    users of Water Dragon to search for their University by acronym.

        Note: This feature may not be added. Django Rest Framework does not
        allow `or` / `Q Object` searches.

    Also, position data is provided to allow `Nationals` to view their
    `Organizations` on a map.
    """
    name = models.CharField(max_length=80, unique=True)
    acronym = models.CharField(max_length=80)
    state = models.CharField(max_length=30)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
 
    class Meta:
        verbose_name_plural = 'Universities'

    def __unicode__(self):
        """
        Return a unicode representation of this model.
        """
        return self.name

"""
                             USER PROFILE MODELS

    The following models represent types of users in the Water Dragon system.

        * Nationals
        * Administrator
        * Host

    Each of these models contain a Foreign Key to the
    custom user model.
"""


class Nationals(models.Model):
    """
    The `Nationals` model represents a user that is the administrator over
    an entire `Organization`. This user manages multiple `Host` users.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    organization = models.ForeignKey(Organization, related_name='nationals')

    enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Nationals'

    def __unicode__(self):
        """
        Return a unicode representation of this model.
        """
        return unicode(self.organization)

    def save(self, *args, **kwargs):
        """
        Link all pre-existing `Host` objects.
        """
        super(Nationals, self).save(*args, **kwargs)

        Host.objects.filter(organization=self.organization).update(nationals=self.id)
        
    def delete(self, *args, **kwargs):
        """
        Delete `User` object.
        """
        self.user.delete()
        super(Nationals, self).delete(*args, **kwargs)

    def number_of_hosts(self):
        """
        Return the total number of `Hosts` associated with this `Nationals`.
        """
        return self.hosts.count()


class Administrator(models.Model):
    """
    The `Administrator` model represents a user that is the administrator at
    of a specific `University`. This user manages multiple `Host` users.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    university = models.ForeignKey(University, related_name='administrators')

    enabled = models.BooleanField(default=False)

    def __unicode__(self):
        """
        Return a unicode representation of this model.
        """
        return unicode(self.university)

    def save(self, *args, **kwargs):
        """
        Link all pre-existing `Host` objects.
        """
        super(Administrator, self).save(*args, **kwargs)

        Host.objects.filter(university=self.university).update(administrator=self.id)

    def delete(self, *args, **kwargs):
        """
        Delete `User` object.
        """
        self.user.delete()
        super(Administrator, self).delete(*args, **kwargs)

    def number_of_hosts(self):
        """
        Return the total number of `Hosts` associated with this `Administrator`.
        """
        return self.hosts.count()


class Host(models.Model):
    """
    The `Host` model represents a user of a specific `Organization` at an
    individual `University`.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    nationals = models.ForeignKey(Nationals, null=True, blank=True, related_name='hosts')
    administrator = models.ForeignKey(Administrator, null=True, blank=True, related_name='hosts')

    organization = models.ForeignKey(Organization, related_name='hosts')
    university = models.ForeignKey(University, related_name='hosts')

    enabled = models.BooleanField(default=False)

    def __unicode__(self):
        """
        Return a unicode representation of this model.
        """
        return '%s of %s' % (self.organization, self.university)

    def save(self, *args, **kwargs):
        """
        Assign `Nationals` and `Administrator` fields if the corresponding
        objects exist.
        """
        nationals = Nationals.objects.filter(organization=self.organization)
        if nationals:
            self.nationals = nationals[0]

        administrator = Administrator.objects.filter(university=self.university)
        if administrator:
            self.administrator = administrator[0]

        super(Host, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Delete `User` object.
        """
        self.user.delete()
        super(Host, self).delete(*args, **kwargs)

    def has_nationals(self):
        """
        Return a boolean based on whether the `Host` object has a
        defined `Nationals`.
        """
        return True if self.nationals else False

    def has_administrator(self):
        """
        Return a boolean based on whether the `Host` object has a
        defined `Administrator`.
        """
        return True if self.administrator else False

"""
                             EMAIL HELPER MODELS

    The following models are used in the process of sending alerts and
    notifications to users.

        * CarbonCopyAddress
"""


class CarbonCopyAddress(models.Model):
    """
    The `CarbonCopyAddress` model represents an extra email address that a
    user would like alerts and notifications to be sent to.
    """
    email = models.EmailField()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='addresses')

    class Meta:
        verbose_name = 'Carbon Copy Address'
        verbose_name_plural = 'Carbon Copy Addresses'
        unique_together = ('user', 'email')

    def __unicode__(self):
        """
        Return a unicode representation of this model.
        """
        return self.email

"""
                             IDENTITY MODELS

    The following models are used in the process of keeping track of each
    individual person at all events, across all hosts in the country. This
    includes keeping a record of their flags.

        * Identity
        * Flag
"""


class Identity(models.Model):
    """
    The `Identity` model represents a unique individual.
    """
    GENDERS = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
   
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    gender = models.CharField(max_length=80, choices=GENDERS)
    dob = models.DateField()

    class Meta:
        verbose_name = 'Identity'
        verbose_name_plural = 'Identities'
        unique_together = ('first_name', 'last_name', 'gender', 'dob')

    def __unicode__(self):
        """
        Return a unicode representation of this model.
        """
        return '%s, %s' % (self.last_name, self.first_name)

    def save(self, *args, **kwargs):
        """
        Normalize `name` fields.
        """
        self.first_name = self.first_name.lower().strip().capitalize()
        self.last_name = self.last_name.lower().strip().capitalize()

        super(Identity, self).save(*args, **kwargs)


class Flag(models.Model):
    """
    Represents a violation by a specific `Identity`. `Flags` can be reported
    by any one of the three user profiles.
    """
    REACH = (
        ('Nationals', 'Nationals'),
        ('Administrator', 'Administrator'),
        ('Host', 'Host')
    )

    VIOLATIONS = (
        ('Underage Drinking', 'Underage Drinking'),
        ('Stealing', 'Stealing'),
        ('Vandalism', 'Vandalism'),
        ('Violence', 'Violence'),
        ('Probation', 'Probation'),
        ('Other', 'Other')
    )

    identity = models.ForeignKey(Identity, related_name='flags')

    nationals = models.ForeignKey(Nationals, related_name='flags', blank=True, null=True)
    administrator = models.ForeignKey(Administrator, related_name='flags', blank=True, null=True)
    host = models.ForeignKey(Host, related_name='flags', blank=True, null=True)

    reach = models.CharField(max_length=80, choices=REACH)
    violation = models.CharField(max_length=80, choices=VIOLATIONS)
    other = models.CharField(max_length=80, blank=True, null=True)

    def __unicode__(self):
        """
        Return a unicode representation of this model.
        """
        return str(self.identity)

    def creator(self):
        """
        Return the corresponding creator of this object.
        """
        if self.nationals is not None:
            return str(self.nationals)
        elif self.administrator is not None:
            return str(self.administrator)
        elif self.host is not None:
            return str(self.host)
        else:
            return None

"""
                             EVENT MODELS

    The following models are used in the process of registering events,
    keeping track of security procedures and building the list of guests the
    user has invited to his/her event.

        * Event
        * Procedure
        * Invitee
"""


class Event(models.Model):
    """
    The `Event` model represents an event that has been created by a `Host`
    object. Each `Event` has a list of `Procedures`, `Invitees` and
    `RegisteredGuests`.
    """
    EXCLUSIVITY = (
        ('Invitation Only', 'Invitation Only'),
        ('Open to the public', 'Open to the public'),
        ('Open to Faculty, Staff, Students', 'Open to Faculty, Staff, Students')
    )

    ENTRY = (
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    name = models.CharField(max_length=80)
    description = models.TextField()

    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=160)

    planner_name = models.CharField(max_length=80)
    planner_mobile = models.CharField(max_length=80)
    planner_email = models.EmailField()

    president_email = models.EmailField()
    sober_monitors = models.TextField()

    expected_guest_count = models.IntegerField()
    exclusivity = models.CharField(max_length=80, choices=EXCLUSIVITY)
    alcohol_distribution = models.TextField(blank=True, null=True)

    entry = models.CharField(max_length=80, choices=ENTRY)
    entry_description = models.CharField(max_length=160)
    
    co_sponsored_description = models.TextField(blank=True, null=True)
    transportation = models.TextField(blank=True, null=True)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    host = models.ForeignKey(Host, related_name='events')

    class Meta:
        unique_together = ('host', 'name', 'date')

    def __unicode__(self):
        """
        Return a unicode representation of this model.
        """
        return "%s's %s" % (str(self.host), self.name)


class Procedure(models.Model):
    """
    Represent a specefic security procedure that will be completed or has
    been completed by a `Host` at an `Event`.
    """
    PROCEDURES = (
        ('Interior Sweep', 'Interior Sweep'),
        ('Exterior Sweep', 'Exterior Sweep')
    )

    description = models.CharField(max_length=80, choices=PROCEDURES)
    completion_time = models.DateTimeField(blank=True, null=True)

    event = models.ForeignKey(Event, related_name='procedures')

    def __unicode__(self):
        """
        Return a unicode representation of this model.
        """
        return str(self.event.name), '-', str(self.description)


class Invitee(models.Model):
    """
    Represents a person denoted by a `first_name`, `last_name`, and `gender`.
    An `Invitee` has arrived at the event, but has been placed on the list of
    guests that have received an invitation to the event.
    """
    GENDERS = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    gender = models.CharField(max_length=80, choices=GENDERS)

    event = models.ForeignKey(Event, related_name='invitees')

    def __unicode__(self):
        """
        Return a unicode respresentation of this model.
        """
        return '%s %s at %s' % (self.first_name, self.last_name, self.event.name)

    def save(self, *args, **kwargs):
        """
        Normalize `name` fields.
        """
        self.first_name = self.first_name.lower().strip().capitalize()
        self.last_name = self.last_name.lower().strip().capitalize()

        super(Invitee, self).save(*args, **kwargs)

"""
                             GUEST REGISTRATION MODEL

    The following model is used to represent the registration a single
    `Identity` to a specific `Event`.

        * GuestRegistration
"""


class GuestRegistration(models.Model):
    """
    The `GuestRegistration` model represnts when a single `Identity` is
    registered to a specific `Event`.
    """
    image = models.ImageField(upload_to='images/guests', storage=MinioStorage())

    identity = models.ForeignKey(Identity, related_name='registrations')
    event = models.ForeignKey(Event, related_name='registrations')

    date_time_taken = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('identity', 'event')

    def __unicode__(self):
        """
        Return a unicode respresentation of this model.
        """
        return '%s at %s' % (str(self.identity), self.event.name)


"""
                             IMPORT RECEIVERS
"""
from api import receivers

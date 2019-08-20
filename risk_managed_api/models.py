from django.conf import settings
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class University(models.Model):
    name = models.CharField(max_length=80, unique=True)
    acronym = models.CharField(max_length=80)
    state = models.CharField(max_length=30)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Universities"

    def __str__(self):
        return self.acronym


class Nationals(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    organization = models.ForeignKey(
        Organization, related_name="nationals", on_delete=models.CASCADE
    )

    enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Nationals"

    def __str__(self):
        return str(self.organization)

    def save(self, *args, **kwargs):
        super(Nationals, self).save(*args, **kwargs)
        Host.objects.filter(organization=self.organization).update(nationals=self.id)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super(Nationals, self).delete(*args, **kwargs)

    def number_of_hosts(self):
        return self.hosts.count()


class Administrator(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    university = models.ForeignKey(
        University, related_name="administrators", on_delete=models.CASCADE
    )

    enabled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.university)

    def save(self, *args, **kwargs):
        super(Administrator, self).save(*args, **kwargs)

        Host.objects.filter(university=self.university).update(administrator=self.id)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super(Administrator, self).delete(*args, **kwargs)

    def number_of_hosts(self):
        return self.hosts.count()


class Host(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    nationals = models.ForeignKey(
        Nationals, null=True, blank=True, related_name="hosts", on_delete=models.CASCADE
    )
    administrator = models.ForeignKey(
        Administrator, null=True, blank=True, related_name="hosts", on_delete=models.CASCADE
    )

    organization = models.ForeignKey(Organization, related_name="hosts", on_delete=models.CASCADE)
    university = models.ForeignKey(University, related_name="hosts", on_delete=models.CASCADE)

    enabled = models.BooleanField(default=False)

    def __str__(self):
        return "%s of %s" % (self.organization, self.university)

    def save(self, *args, **kwargs):
        nationals = Nationals.objects.filter(organization=self.organization).first()
        if nationals:
            self.nationals = nationals

        administrator = Administrator.objects.filter(university=self.university).first()
        if administrator:
            self.administrator = administrator

        super(Host, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super(Host, self).delete(*args, **kwargs)

    def has_nationals(self):
        return bool(self.nationals_id)

    def has_administrator(self):
        return bool(self.administrator_id)


class CarbonCopyAddress(models.Model):
    email = models.EmailField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="addresses", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Carbon Copy Address"
        verbose_name_plural = "Carbon Copy Addresses"
        unique_together = ("user", "email")

    def __str__(self):
        return self.email


class Identity(models.Model):
    GENDERS = (("Male", "Male"), ("Female", "Female"))

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    gender = models.CharField(max_length=80, choices=GENDERS)
    dob = models.DateField()

    class Meta:
        verbose_name = "Identity"
        verbose_name_plural = "Identities"
        unique_together = ("first_name", "last_name", "gender", "dob")

    def __str__(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.lower().strip().capitalize()
        self.last_name = self.last_name.lower().strip().capitalize()
        super(Identity, self).save(*args, **kwargs)


class Flag(models.Model):
    REACH = (("Nationals", "Nationals"), ("Administrator", "Administrator"), ("Host", "Host"))

    VIOLATIONS = (
        ("Underage Drinking", "Underage Drinking"),
        ("Stealing", "Stealing"),
        ("Vandalism", "Vandalism"),
        ("Violence", "Violence"),
        ("Probation", "Probation"),
        ("Other", "Other"),
    )

    identity = models.ForeignKey(Identity, related_name="flags", on_delete=models.CASCADE)

    nationals = models.ForeignKey(
        Nationals, related_name="flags", blank=True, null=True, on_delete=models.CASCADE
    )
    administrator = models.ForeignKey(
        Administrator, related_name="flags", blank=True, null=True, on_delete=models.CASCADE
    )
    host = models.ForeignKey(
        Host, related_name="flags", blank=True, null=True, on_delete=models.CASCADE
    )

    reach = models.CharField(max_length=80, choices=REACH)
    violation = models.CharField(max_length=80, choices=VIOLATIONS)
    other = models.CharField(max_length=80, blank=True, null=True)

    def __str__(self):
        return str(self.identity)

    def creator(self):
        if self.nationals is not None:
            return str(self.nationals)
        elif self.administrator is not None:
            return str(self.administrator)
        elif self.host is not None:
            return str(self.host)
        else:
            return None


class Event(models.Model):
    EXCLUSIVITY = (
        ("Invitation Only", "Invitation Only"),
        ("Open to the public", "Open to the public"),
        ("Open to Faculty, Staff, Students", "Open to Faculty, Staff, Students"),
    )

    ENTRY = (("Yes", "Yes"), ("No", "No"))

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

    host = models.ForeignKey(Host, related_name="events", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("host", "name", "date")

    def __str__(self):
        return "%s's %s" % (str(self.host), self.name)


class Procedure(models.Model):

    PROCEDURES = (("Interior Sweep", "Interior Sweep"), ("Exterior Sweep", "Exterior Sweep"))

    description = models.CharField(max_length=80, choices=PROCEDURES)
    completion_time = models.DateTimeField(blank=True, null=True)

    event = models.ForeignKey(Event, related_name="procedures", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.event.name), "-", str(self.description)


class Invitee(models.Model):
    GENDERS = (("Male", "Male"), ("Female", "Female"))

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    gender = models.CharField(max_length=80, choices=GENDERS)

    event = models.ForeignKey(Event, related_name="invitees", on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s at %s" % (self.first_name, self.last_name, self.event.name)

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.lower().strip().capitalize()
        self.last_name = self.last_name.lower().strip().capitalize()
        super(Invitee, self).save(*args, **kwargs)


class GuestRegistration(models.Model):
    image = models.ImageField(upload_to="images/guests")

    identity = models.ForeignKey(Identity, related_name="registrations", on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name="registrations", on_delete=models.CASCADE)

    date_time_taken = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("identity", "event")

    def __str__(self):
        return "%s at %s" % (str(self.identity), self.event.name)

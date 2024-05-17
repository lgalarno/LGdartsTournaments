from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db import models
from django.shortcuts import reverse

from datetime import datetime
from zoneinfo import ZoneInfo
import os
import pytz


# Create your models here.

class User(AbstractUser):
    TIMEZONES = tuple(zip(pytz.common_timezones, pytz.common_timezones))
    time_zone = models.CharField(max_length=32, choices=TIMEZONES, default='UTC')
    city = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return self.username

    def get_datetime_local(self, is_now=False, dt=None):
        """
        Transform a datetime object to a local datetime according to the user preference saved in time_zone. Must
        provide either is_now=True or a dt. Using is_now=False without a dt will return None.
        :param is_now: get a local datetime for 'now'. dt is ignored
        :param dt: provide a datetime object
        :return: datetime object in the user's tz
        """
        tz = self.time_zone
        if not tz:
            tz = 'UTC'
        if is_now:
            return datetime.now(ZoneInfo(tz))
        elif dt:
            return dt.replace(tzinfo=ZoneInfo(tz))
        else:
            return None


def upload_location(instance, filename):
    return f"{instance}/{filename}"


class Darts(models.Model):
    name = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(User, related_name="darts", on_delete=models.CASCADE)
    weight = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    picture = models.ImageField(upload_to=upload_location,
                                null=True,
                                blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Darts"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('accounts:darts-detail', kwargs={'pk': self.pk})


@receiver(models.signals.post_delete, sender=Darts)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Player` object is deleted.
    """
    if instance.picture:
        if os.path.isfile(instance.picture.path):
            os.remove(instance.picture.path)


@receiver(models.signals.pre_save, sender=Darts)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `Player` object is updated
    with new file.
    """
    if not instance.pk:
        return False
    try:
        old_picture = Darts.objects.get(pk=instance.pk).picture
    except Darts.DoesNotExist:
        return False

# TODO make it better...
    new_picture = instance.picture
    if not bool(old_picture):
        return False
    if not old_picture == new_picture:
        if os.path.isfile(old_picture.path):
            os.remove(old_picture.path)

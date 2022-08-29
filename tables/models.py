from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# Create your models here.

class Zipcsvfile(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    filename = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32)
    path = models.FileField()
    timesdownloaded = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return self.filename

    def get_absolute_url(self):
        return reverse('tables:download-zip', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        '''
        On save,
        create slug
        update timestamps to user's tz
        '''
        if not self.id:
            self.slug = slugify(self.filename)
        # tz = self.user.time_zone
        # if not tz:
        #     tz = 'UTC'
        # now = timezone.now()
        now = self.user.get_datetime_local(is_now=True, dt=None)
        self.timestamp = now  # timezone.localtime(now, pytz.timezone(tz))
        super(Zipcsvfile, self).save(*args, **kwargs)

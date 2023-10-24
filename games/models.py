from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils import timezone
from accounts.models import Darts, User


# Create your models here.

class GameType(models.Model):
    GAMETYPE_CHOICES = (
        ('BB', 'Baseball'),
        ('501', '501'),
        ('Cricket', 'Cricket'),
    )
    SCORING_CHOICES = (
        ('Ranks', 'Ranks'),
        ('Points', 'Points and ranks'),
    )
    name = models.CharField(choices=GAMETYPE_CHOICES, max_length=16)
    scoring = models.CharField(choices=SCORING_CHOICES, max_length=16)

    def __str__(self):
        return self.name


class Tournament(models.Model):
    SCHEDULING = (
        ('Continual', 'Going on until deactivation'),
        # ('Determined', 'Fixed number of games'),
        ('Round-robin', 'Round-robin (each contestant meets every other participant)'),
    )
    MATCHING = (
        ('all', 'All participants play every games'),
        ('pairs', 'Head to head games'),
    )
    name = models.CharField(max_length=255)
    gametype = models.ForeignKey(to=GameType, default=1, on_delete=models.CASCADE, related_name='gametype', blank=False)
    # TODO check if blank=False still require self.fields['scheduling'].empty_label = None
    scheduling = models.CharField(choices=SCHEDULING, default='Continual', max_length=16, blank=False)
    matching = models.CharField(choices=MATCHING, default='all', max_length=16, blank=False)
    number_of_rounds = models.IntegerField(null=True, blank=True)
    darts = models.ManyToManyField(to=Darts, related_name="darts")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=False)
    editable = models.BooleanField(default=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('games:update-tournament', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('games:delete-tournament', kwargs={'pk': self.pk})

    def get_number_of_games(self):
        return self.game_set.all().count()

    def get_number_of_players(self):
        return self.darts.all().count()


class Game(models.Model):
    datetime = models.DateTimeField(blank=True, null=True)
    tournament = models.ForeignKey(to=Tournament, on_delete=models.CASCADE)
    round = models.IntegerField(blank=True, null=True)
    played = models.BooleanField(default=False)

    class Meta:
        ordering = ['-datetime', 'round']

    def __str__(self):
        return f"{self.tournament}-{self.round}-{self.datetime}"

    def get_absolute_url(self):
        return reverse('games:edit-game', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('games:delete-game', kwargs={'pk': self.pk})

    @property
    def get_datetime(self):
        return timezone.localtime(self.datetime)

    def get_all_players(self):
        return [darts.darts.name for darts in self.participant_set.all()]

    def get_number_of_players(self):
        return len(self.get_all_players())

    def get_ranks(self):
        return {p.darts.name: p.rank for p in self.participant_set.all()}

    def get_scores(self):
        return {p.darts.name: p.score for p in self.participant_set.all()}

    def get_points(self):
        return {p.darts.name: self.get_number_of_players() + 1 - p.rank for p in self.participant_set.all()}

    def get_ranking(self):
        """
        Format the rank columns in the following style according to the
        selected rank for each player and return a dictionary
        PP	        HH22	HH18
        PP+HH18		      HH22
        m is the max number of players in all the tables
        """
        d = self.get_ranks()
        return ['+'.join(p for p in d if d[p] == k) for k in range(1, self.get_number_of_players() + 1)]


# # method to find_if_the_game_was_played
@receiver(post_save, sender=Game, dispatch_uid="find_if_the_game_was_played")
def updategame_played(sender, instance, **kwargs):
    r = instance.get_ranks()
    if None in r.values() and instance.played is True:
        instance.played = False
        instance.save()


class Participant(models.Model):
    darts = models.ForeignKey(to=Darts, on_delete=models.CASCADE)
    game = models.ForeignKey(to=Game, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.darts} in {self.game}"

from django import forms

from accounts.models import Darts
from .models import Tournament, Game, Participant


class TournamentCreateForm(forms.ModelForm):

    class Meta:
        model = Tournament
        fields = (
            'name',
            'gametype',
            'darts',
            'city',
            'country',
        )

        labels = {
            "name": "Tournament name",
            "gametype": "Type of game",
            "darts": "Participants",
        }

    def __init__(self, *args, **kwargs):
        # editable = kwargs.pop('editable', True)
        user = kwargs.pop('user', None)
        super(TournamentCreateForm, self).__init__(*args, **kwargs)
        if not user:
            user = self.instance.user
        self.fields['darts'].queryset = Darts.objects.filter(user=user).filter(active=True)
        # if not editable:
        #     self.fields['gametype'].disabled = True
        #     # self.fields['matching'].disabled = True
        #     # self.fields['category'].disabled = True
        #     self.fields['darts'].disabled = True


class TournamentUpdateForm(forms.ModelForm):

    class Meta:
        model = Tournament
        fields = (
            'name',
            'gametype',
            'matching',
            'scheduling',
            'darts',
            'city',
            'country',
            'start_date',
            'active'
        )
        labels = {
            "name": "Tournament name",
            "gametype": "Type of game",
            'matching': 'Type of matching (all participants or pairs',
            "scheduling": "Scheduling option",
            "darts": "Participants",
            "start_date": "Starting date",
            "active": "Tournament still ongoing?"
        }

    def __init__(self, *args, **kwargs):
        super(TournamentUpdateForm, self).__init__(*args, **kwargs)
        self.fields['darts'].queryset = Darts.objects.filter(user=self.instance.user).filter(active=True)
        self.fields['gametype'].disabled = True
        self.fields['matching'].disabled = True
        self.fields['scheduling'].disabled = True
        self.fields['darts'].disabled = True


class TournamentCreateNextForm(forms.ModelForm):

    class Meta:
        model = Tournament
        fields = (
            'matching',
            'scheduling',
            'start_date',
            'active'
        )

        labels = {
            'matching': 'Type of matching (all participants or pairs',
            "scheduling": "Scheduling option",
            "start_date": "Starting date",
            "active": "Tournament active?"
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(TournamentCreateNextForm, self).__init__(*args, **kwargs)
        self.fields['matching'].empty_label = "None"
        self.fields['scheduling'].empty_label = None


class GameForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = (
            'tournament',
            # 'number',
            'datetime',
        )
        labels = {
            "tournament": "Tournament",
            # "number": "Number",
            "datetime": "Date and time (format: 2022-08-24 20:43:55)",
        }
        widgets = {
            'tournament': forms.HiddenInput(),
        }


class ParticipantForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = ['darts',
                  'score',
                  'rank', ]
        labels = {
            "darts": "Darts",
            "score": "Score",
            "rank": "Rank",
        }
        # widgets = {'rank': forms.ChoiceField()}

    def __init__(self, *args, **kwargs):
        game_type = kwargs.pop('game_type', None)
        darts_qs = kwargs.pop('darts_qs', None)
        super(ParticipantForm, self).__init__(*args, **kwargs)
        if darts_qs:
            self.fields['darts'].queryset = darts_qs
            self.fields['darts'].empty_label = None
            ranks_ckoices =  [(str(i), i) for i in range(1, len(darts_qs)+1)]
            self.fields['rank'] = forms.ChoiceField(choices=ranks_ckoices)
            # TODO should not be hardcoded. ..gametype in [] set of gametype wher score should be disabled?
            if game_type == '501':
                self.fields['score'].widget = forms.HiddenInput()
            else:
                self.fields['rank'].widget = forms.HiddenInput()


# TODO randomize games
class RoundRobinCreateForm(forms.Form):
    RANDOM_CHOICES = [
        ('rnd-no', 'No round randomization'),
        ('rnd-half', 'Randomize each half'),
        ('rnd-all', 'Randomize all rounds'),
    ]
    nfullrounds = forms.IntegerField(min_value=1, label="Number of full rounds")
    rndounds = forms.CharField(label='What type of rounds randomization?', widget=forms.RadioSelect(choices=RANDOM_CHOICES))
    tournament = forms.HiddenInput()

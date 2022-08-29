from django import forms

from .models import Tournament, Game, Participant


class TournamentForm(forms.ModelForm):

    class Meta:
        model = Tournament
        fields = (
            'name',
            'gametype',
            'matching',
            'category',
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
            "category": "Category",
            "darts": "Participants",
            "start_date": "Starting date",
            "active": "Tournament still ongoing?"
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        editable = kwargs.pop('editable', True)
        super(TournamentForm, self).__init__(*args, **kwargs)
        if not editable:
            self.fields['gametype'].disabled = True
            self.fields['matching'].disabled = True
            self.fields['category'].disabled = True
            self.fields['darts'].disabled = True


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
            #darts_qs = tournament.darts.all()
            self.fields['darts'].queryset = darts_qs
            self.fields['darts'].empty_label = None
            ranks_ckoices =  [(str(i), i) for i in range(1, len(darts_qs)+1)]
            self.fields['rank'] =  forms.ChoiceField(choices=ranks_ckoices)
            # TODO should not be hardcoded. ..gametype in [] set of gametype wher score should be disabled?
            if game_type == '501':
                self.fields['score'].widget = forms.HiddenInput()
            else:
                self.fields['rank'].widget = forms.HiddenInput()
                # self.fields['rank'].initial = None

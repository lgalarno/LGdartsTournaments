from django import forms

from tournaments.models import Game, Participant


class RRGameForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = (
            'tournament',
        )
        labels = {
            "tournament": "Tournament",
        }
        widgets = {
            'tournament': forms.HiddenInput(),
        }


class RRParticipantForm(forms.ModelForm):
    RESULT = (
        ('', '----'),
        ('2', 'Win'),
        ('1', 'Draw'),
        ('0', 'Lose'),
    )

    class Meta:
        model = Participant
        fields = ['darts',
                  'score',
                  'rank', ]
        widgets = {'darts': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        game_type = kwargs.pop('game_type', None)
        super(RRParticipantForm, self).__init__(*args, **kwargs)
        self.fields['rank'] = forms.ChoiceField(choices=self.RESULT)

        if game_type == '501':
            self.fields['score'].widget = forms.HiddenInput()
            # self.fields['rank'].label = "Result"
        else:
            self.fields['rank'].widget = forms.HiddenInput()
        for f in self.fields:
            self.fields[str(f)].label = ""
            self.fields[str(f)].widget.attrs.update({'style': "width: 5em;"})

    def clean(self):
        print(self.game_type)


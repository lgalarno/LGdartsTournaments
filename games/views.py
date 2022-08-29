from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView

from accounts.models import Darts, User

from .forms import TournamentForm, GameForm, ParticipantForm
from .models import Game, Tournament, Participant

# Create your views here.


class TournamentListView(LoginRequiredMixin, ListView):
    model = Tournament

    def get_queryset(self):
        return Tournament.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'list-tournaments'
        return context


class CreateTournament(LoginRequiredMixin, CreateView):
    context_object_name = 'Create'
    model = Tournament
    form_class = TournamentForm

    def get_form(self):
        form = super().get_form()
        form.fields['darts'] = forms.ModelMultipleChoiceField(
            queryset=Darts.objects.filter(user=self.request.user).filter(active=True)
        )
        return form

    def get_initial(self):
        u = get_object_or_404(User, id=self.request.user.pk)
        now = u.get_datetime_local(is_now=True, dt=None)
        return {
            'start_date': now.date(),
            'city': self.request.user.city,
            'country': self.request.user.country,
        }

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'create-tournament'
        return context


class TournamentDetailView(DetailView):
    model = Tournament

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'tournament-detail'
        return context


class TournamentUpdateView(LoginRequiredMixin, UpdateView):
    model = Tournament
    form_class = TournamentForm

    def get_form(self):
        form = super().get_form()
        if self.object.editable:
            form.fields['darts'] = forms.ModelMultipleChoiceField(
                queryset=Darts.objects.filter(user=self.request.user).filter(active=True)
            )
        return form

    def get_form_kwargs(self):
        kwargs = super(TournamentUpdateView, self).get_form_kwargs()
        kwargs['editable'] = self.object.editable
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'update-tournament'
        context['deleteURL'] = self.object.get_delete_url()
        return context


class TournamentDeleteView(LoginRequiredMixin, DeleteView):
    model = Tournament
    success_url = reverse_lazy('games:list-tournaments')


class AllTournamentsListView(ListView):
    model = Tournament
    paginate_by = 20
    template_name = 'games/all_tournaments_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'list-all-tournaments'
        return context


def tournament_games(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    games = tournament.game_set.all().order_by('-datetime')
    if games:
        nplayers = games.first().get_number_of_players()
        nplayerslist = [i + 1 for i in range(nplayers)]
    context = {
        "title": "tournament-tables",
        "tournament": tournament,
        "tables": games,
        'nplayerslist': nplayerslist
    }
    return render(request, f'games/tournament_games.html', context)


def game_create(request, tournament_id=None):
    new_result_btn = False
    tournament = get_object_or_404(Tournament, id=tournament_id)

    darts = tournament.darts.all()
    if tournament.matching == 'all':
        max = len(darts)
        extra = 0
        initial_formset = [{'darts': d.id} for d in darts]
    elif tournament.matching == 'pairs':
        max = 2
        extra = 2
        initial_formset = None
    else:
        return HttpResponseBadRequest(f'The matching type of {tournament.name} is improperly configured', status=400)
    u = get_object_or_404(User, id=tournament.user_id)
    now = u.get_datetime_local(is_now=True, dt=None)

    initial_dict = {
        "tournament": tournament.id,
        "datetime": now,
    }
    form_game = GameForm(request.POST or None, initial=initial_dict)
    formset = forms.formset_factory(form=ParticipantForm, extra=extra, max_num=max)
    participant_formset = formset(request.POST or None,
                                  initial=initial_formset,
                                  form_kwargs={'darts_qs': darts,
                                               'game_type': tournament.gametype.name})
    if all([form_game.is_valid(), participant_formset.is_valid()]):
        parent = form_game.save(commit=False)
        parent.save()
        participants = []
        for form in participant_formset:
            child = form.save(commit=False)
            participants.append(child.darts.name)
            child.game = parent
            child.save()
        if tournament.editable:
            tournament.editable = False
            tournament.save()
            new_result_btn = True

    if request.META.get("HTTP_REFERER") != request.build_absolute_uri():
        back_link = request.META.get("HTTP_REFERER")
    else:
        back_link = reverse("tables:tournament-tables", kwargs={'tournament_id': tournament.id,
                                                                'tbl_type': 'ranks'})
    context = {
        'tournament': tournament,
        'back_link': back_link,
        'form': form_game,
        'new_result_btn': new_result_btn,
        'participant_formset': participant_formset
        }
    return render(request, 'games/game-create.html', context)


def delete_game(request, pk):
    game = get_object_or_404(Game, id=pk)
    tournament = get_object_or_404(Tournament, id=game.tournament.id)
    game.delete()
    if tournament.get_number_of_games() == 0:
        tournament.editable = True
        tournament.save()

    if request.META.get("HTTP_REFERER") != request.build_absolute_uri():
        # Try if the referer != the link to delete. If yes, go back there.
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        # Else, go to the tournament's ranks table
        return HttpResponseRedirect(reverse("tables:tournament-tables", kwargs={'tournament_id': tournament.id,
                                                                                'tbl_type': 'ranks'}))


class GameUpdateView(LoginRequiredMixin, UpdateView):
    model = Game
    form_class = GameForm

    def form_valid(self, form):
        context = self.get_context_data()
        participant_formset = context['participant_formset']

        with transaction.atomic():
            self.object = form.save()
            if participant_formset.is_valid():
                participant_formset.instance = self.object
                participant_formset.save()
        return super(GameUpdateView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        darts = self.object.tournament.darts.all()
        participants = self.object.participant_set.all()
        max = len(darts)
        formset = modelformset_factory(Participant, form=ParticipantForm, extra=0, max_num=max)
        if self.request.POST:
            participant_formset = formset(self.request.POST, form_kwargs={'darts_qs': darts,
                                                                          'game_type': self.object.tournament.gametype})
        else:
            participant_formset = formset(queryset=participants, form_kwargs={'darts_qs': darts,
                                                                              'game_type': self.object.tournament.gametype.name})
        context["participant_formset"] = participant_formset
        context['tournament'] = self.object.tournament
        context['title'] = 'update-game'
        context['deleteURL'] = self.object.get_delete_url()
        return context


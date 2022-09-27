from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse, redirect
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView

from accounts.models import Darts, User

from .backend import create_balanced_round_robin

from .forms import (TournamentCreateForm,
                    GameForm,
                    ParticipantForm,
                    TournamentUpdateForm,
                    TournamentCreateNextForm,
                    RoundRobinCreateForm)
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
    form_class = TournamentCreateForm

    # def get_form(self):
    #     form = super().get_form()
    #     form.fields['darts'] = forms.ModelMultipleChoiceField(
    #         queryset=Darts.objects.filter(user=self.request.user).filter(active=True)
    #     )
    #     return form

    def get_form_kwargs(self):
        kwargs = super(CreateTournament, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        # u = get_object_or_404(User, id=self.request.user.pk)
        # now = u.get_datetime_local(is_now=True, dt=None)
        return {
            # 'start_date': now.date(),
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

    def get_success_url(self):
        return reverse_lazy('games:create-tournaments-next', kwargs={'tournament_id': self.object.pk})


def update_tournament(request, pk=None):
    tournament = get_object_or_404(Tournament, id=pk, user=request.user)
    if tournament.editable:
        form = TournamentCreateForm(request.POST or None, instance=tournament)
        if form.is_valid():
            form.save()
            return redirect('games:create-tournaments-next', tournament_id=tournament.id)
    else:
        form = TournamentUpdateForm(request.POST or None, instance=tournament)
    if form.is_valid():
        form.save()
    context = {
        "title": "create_tournament",
        'form': form,
        "tournament": tournament,
    }
    return render(request, 'games/tournament_form.html', context)


def create_tournament_next(request, tournament_id=None):
    tournament = Tournament.objects.get(id=tournament_id)
    u = get_object_or_404(User, id=request.user.pk)
    now = u.get_datetime_local(is_now=True, dt=None)
    form = TournamentCreateNextForm(request.POST or None,  instance=tournament, initial={'start_date': now.date(),
                                                                                         'active': True
                                                                                         })
    if form.is_valid():
        form.save()
    if request.method == "POST" and tournament.scheduling == 'Round-robin':
        return HttpResponseRedirect(reverse("games:create-round-robin", kwargs={'tournament_id': tournament.id}))
        # return render(request, 'games/create-round-robin.html', context)

    context = {
        "title": "create_tournament_next",
        'form': form,
        "tournament": tournament,
    }
    return render(request, 'games/create_tournament_next.html', context)


def create_tournament_rr(request, tournament_id=None):
    tournament = Tournament.objects.get(id=tournament_id)
    form = RoundRobinCreateForm(request.POST or None, initial={'tournament': tournament.id,
                                                               'nfullrounds': 2,
                                                               'rndounds': 'rnd-no'
                                                               })
    context = {
        "title": "create-round-robin",
        'form': form,
        "tournament": tournament,
    }
    if request.method == "POST":
        darts = tournament.darts.all()
        players = [d.name for d in darts]
        nfullrounds = form["nfullrounds"].value()  # request.POST.get('number-rounds', None)
        s = create_balanced_round_robin(players, nfullrounds)
        request.session['schedule'] = s
        context['schedule'] = s
    return render(request, 'games/create-round-robin.html', context)


def save_tournament_rr(request, tournament_id=None):
    tournament = Tournament.objects.get(id=tournament_id)

    context = {
        "title": "create-round-robin",
        "tournament": tournament,
    }
    schedule = request.session.get("schedule", None)
    if schedule:
        tournamentdarts = tournament.darts.all()
        context["schedule"] = schedule
        for round, games in schedule.items():
            for game in games:
                g = Game(tournament=tournament,
                         played=False,
                         round=int(round.split('-')[1]))
                g.save()
                for darts in game:
                    try:
                        d = tournamentdarts.get(name=darts)
                        p = Participant(game=g,
                                        darts=d
                                        )
                        p.save()
                    except:
                        return HttpResponse(status=500)
        games = tournament.game_set.all().order_by('round')
        tournament.number_of_rounds = games.last().round
        tournament.editable = False
        tournament.save()
        return render(request, 'games/rr-view-games.html', context)
    else:
        return Http404


class TournamentDetailView(DetailView):
    model = Tournament

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'tournament-detail'
        return context


class TournamentUpdateView(LoginRequiredMixin, UpdateView):
    model = Tournament
    form_class = TournamentCreateForm

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

    def get_success_url(self):
        return reverse_lazy('games:create-tournaments-next', kwargs={'tournament_id': self.object.pk})


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
    initial_dict = {
        "tournament": tournament.id,
        "datetime": timezone.localtime(timezone.now())
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
        for form in participant_formset:
            child = form.save(commit=False)
            child.game = parent
            child.save()
        if tournament.editable:
            tournament.editable = False
            tournament.save()
        new_result_btn = True
        messages.success(request, "The game was saved.")

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
    return render(request, 'games/game_form.html', context)


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
                messages.success(self.request, "The game was updated.")
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

        if self.request.META.get("HTTP_REFERER") != self.request.build_absolute_uri():
            back_link = self.request.META.get("HTTP_REFERER")
        else:
            back_link = reverse("tables:tournament-tables", kwargs={'tournament_id':self. object.tournament.id,
                                                                    'tbl_type': 'ranks'})
        context["participant_formset"] = participant_formset
        context['tournament'] = self.object.tournament
        context['back_link'] = back_link
        context['title'] = 'update-game'
        context['deleteURL'] = self.object.get_delete_url()
        return context

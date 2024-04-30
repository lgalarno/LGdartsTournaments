from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.encoding import smart_str

from datetime import datetime

import csv
import os
import zipfile

from accounts.models import User
from tournaments.models import Tournament, Game


from .backend import rankstable, bb_score_tables, write_csv, round_robin_formset
from .models import Zipcsvfile


# Create your views here.

def tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    games = tournament.game_set.all().order_by('-datetime')
    games_headers, games_tbl, standings_headers, standings_tbl = rankstable(games, tournament)
    if tournament.gametype.name == 'BB' or tournament.gametype.name == 'Cricket':
        scores_headers, scores_tbl, avg_headers, avg_tbl = bb_score_tables(games, tournament)
    else:
        scores_headers = scores_tbl = avg_headers = avg_tbl = False
    context = {
        "tournament": tournament,
        'games_headers': games_headers,
        'games_tbl': games_tbl,
        'standings_headers': standings_headers,
        'standings_tbl': standings_tbl,
        'scores_headers': scores_headers,
        'scores_tbl': scores_tbl,
        'avg_headers': avg_headers,
        'avg_tbl': avg_tbl
    }
    return render(request, f'tables/tournament.html', context)


def tournament_tables(request, tournament_id, tbl_type):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    games = tournament.game_set.all().order_by('-datetime')
    if tbl_type == 'ranks':
        main_headers, main_tbl, summary_headers, summary_tbl = rankstable(games, tournament)
        stable_title = 'Standings'
    elif tbl_type == 'scores':
        main_headers, main_tbl, summary_headers, summary_tbl = bb_score_tables(games, tournament)
        stable_title = 'Average scores'
    else:
        raise Http404("This page does not exist")
    context = {
        "tbl_type": tbl_type,
        "tournament": tournament,
        'main_headers': main_headers,
        'main_tbl': main_tbl,
        'summary_headers': summary_headers,
        'summary_tbl': summary_tbl,
        'stable_title': stable_title
    }
    return render(request, f'tables/tournament-tables.html', context)


def tournament_rr_tables(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    gametype = str(tournament.gametype)
    if request.method == "POST":
        ok = True
        gamenumber = request.POST.get('submit', None)
        if gamenumber is None:
            raise Http404("No game selected")
        game = get_object_or_404(Game, id=gamenumber)
        game_participants = game.participant_set.all()
        participant_ids = request.POST.getlist('darts', None)
        try:
            p1 = game_participants.get(darts=participant_ids[0])
            p2 = game_participants.get(darts=participant_ids[1])
        except:
            raise Http404("The participants don't exist")
        if gametype != "501":
            """
            if BB or Cricket, set the scores to participants and attribute the ranks
            """
            scores = request.POST.getlist('score', None)
            if "" in scores:
                messages.warning(request, "All the scores for the game should be entered")
                ok = False
            else:
                p1.score = scores[0]
                p2.score = scores[1]
                if scores[0] > scores[1]:
                    p1.rank = 2
                    p2.rank = 0
                elif scores[1] > scores[0]:
                    p1.rank = 0
                    p2.rank = 2
                elif scores[1] == scores[0]:
                    p1.rank = 1
                    p2.rank = 1
        else:
            ranks_str = request.POST.getlist('rank', None)
            ranks = [int(r) for r in ranks_str]
            if sum(ranks) != 2:
                messages.warning(request, "Win, Draw, Lose status for the game is inconsistent")
                ok = False
            else:
                p1.rank = ranks[0]
                p2.rank = ranks[1]
        if ok:
            p1.save()
            p2.save()
            game.datetime = datetime.now()  # u.get_datetime_local(is_now=True, dt=None)
            game.played = True
            game.save()

    formset_dict, standings_headers, standings_tbl = round_robin_formset(tournament)
    context = {
        "title": "round-robin-table",
        'schedule': formset_dict,
        'standings_headers': standings_headers,
        'standings_tbl': standings_tbl,
        "tournament": tournament,
    }
    return render(request, f'tables/tournament-rr-tables.html', context)


#TODO export rr tournaments in csv
def export_csv(request, tournament_id, tbl_type):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    games = tournament.game_set.all().order_by('-datetime')
    if tbl_type == 'ranks':
        main_headers, main_tbl, summary_headers, summary_tbl = rankstable(games, tournament)
    elif tbl_type == 'scores':
        main_headers, main_tbl, summary_headers, summary_tbl = bb_score_tables(games, tournament)
    else:
        raise Http404("This page does not exist")

    u = get_object_or_404(User, id=request.user.pk)
    now = u.get_datetime_local(is_now=True, dt=None)   # datetime.now(pytz.utc)
    # localdt = u.get_datetime_local(now)
    sd = now.date()  # get_date_now(request.user)
    fn = f"{tournament.name}-{tournament.gametype}-{tbl_type}-{sd}.csv"
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{fn}"'
    writer = csv.writer(response)
    writer.writerow(main_headers)
    writer.writerows(main_tbl.values())
    writer.writerows([''])
    writer.writerow(summary_headers)
    writer.writerows(summary_tbl)
    writer.writerows([''])
    return response


def export_zip(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    games = tournament.game_set.all().order_by('-datetime')

    u = get_object_or_404(User, id=request.user.pk)
    now = u.get_datetime_local(is_now=True, dt=None)
    datesuffix = now.date()

    path = os.path.join(settings.MEDIA_ROOT, f'{request.user.username}-files')
    zipfilename = f"{tournament.name}-{tournament.gametype}-{datesuffix}.zip"
    try:
        if not os.path.exists(path):
            os.makedirs(path)

        longzipfilename = os.path.join(path, zipfilename)

        zip_archive = zipfile.ZipFile(longzipfilename, 'w')
        main_headers, main_tbl, summary_headers, summary_tbl = rankstable(games, tournament)
        if len(main_tbl) > 0:
            outfile = f"{tournament.name}-{tournament.gametype}-ranks-{datesuffix}.csv"
            mf = write_csv(main_headers, main_tbl, summary_headers, summary_tbl)
            zip_archive.writestr(outfile, mf.read())
        if len(main_tbl) > 0 and tournament.gametype.name == 'BB':
            main_headers, main_tbl, summary_headers, summary_tbl = bb_score_tables(games, tournament)
            outfile = f"{tournament.name}-{tournament.gametype}-scores-{datesuffix}.csv"
            mf = write_csv(main_headers, main_tbl, summary_headers, summary_tbl)
            zip_archive.writestr(outfile, mf.read())
        zip_archive.close()
    except:
        return HttpResponse(status=500)
    z, created = Zipcsvfile.objects.get_or_create(filename=zipfilename, user=request.user)
    z.path = smart_str(longzipfilename)

    z.filename = zipfilename
    z.timesdownloaded = 0
    z.save()
    userfiles = Zipcsvfile.objects.filter(user=request.user)
    context = {'title': 'Download',
               'allfiles': userfiles
               }
    return render(request, 'tables/download.html', context)


def downloadzip(request, slug=None):
    zf = get_object_or_404(Zipcsvfile, slug=slug)
    link = zf.path
    f = open(smart_str(link), 'rb').read()
    response = HttpResponse(
        f,
        content_type='text/csv',
        headers={'Content-Disposition': f"attachment; filename = {zf.filename}"},
    )
    zf.timesdownloaded += 1
    zf.save()
    return response


def deletezip(request, pk):
    q = get_object_or_404(Zipcsvfile, pk=pk)
    q.path.delete()
    q.delete()
    qs = Zipcsvfile.objects.all().order_by("-timestamp")
    context = {'title': 'Download',
               'allfiles': qs
               }
    return render(request, 'tables/download.html', context)

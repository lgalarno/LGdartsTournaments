from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse
from django.utils.encoding import smart_str

import csv
import os
import zipfile

from accounts.models import User
from games.models import Tournament

from .backend import rankstable, bb_score_tables, write_csv
from .models import Zipcsvfile


# Create your views here.

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


def tournament_wdl(request, tournament_id):
    return HttpResponse('To come...')


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
    f = get_object_or_404(Zipcsvfile, slug=slug)
    link = f.path
    response = HttpResponse()
    response['Content-Type'] = 'application/zip'
    response['Content-Disposition'] = f"attachment; filename = {f.filename}"
    response['X-Sendfile'] = smart_str(link)
    f.timesdownloaded += 1
    f.save()
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

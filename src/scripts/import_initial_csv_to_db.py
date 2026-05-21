from django.utils import timezone

from accounts.models import Darts, User
from tournaments.models import Game, Participant, Tournament, GameType

from datetime import datetime
from zoneinfo import ZoneInfo

import csv


def csv_to_db(f, darts):
    """
    Import previous data from a csv file to the db
    format should be:
    type  #       date   time   ranks or scores
    501	114	2018-01-07	23:52	2	3	1
    BB	  1	2016-03-04	23:34	46	47	42
    the three last columns contains the score/rank. Order properly!!!
    """
    #try:
    with open(f) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            print(f'importing {row}')
            if len(row) > 1:
                dt = _get_dt(row[2], row[3])
                gametype = row[0]
                t = _get_tournament(gametype)
                print(f'tournament name: {t.name}')
                g = Game(datetime=dt,
                         tournament=t,
                         played=True)
                g.save()
                print('bbbb')
                pscore = [row[4 + i] for i in range(0, 3)]
                if gametype == 'BB':
                    pranks = ranking(pscore)
                else:
                    pranks = list(pscore)
                    pscore = [None for i in range(len(pscore))]

                for i, d in enumerate(darts):
                    participant = Participant(game=g,
                                              rank=pranks[i],
                                              score=pscore[i],
                                              darts=d)
                    participant.save()
    #except:
        #return False
    return True


def _get_tournament(type):
    if type == 'BB':
        tname = 'LG_BB'
    elif type == '501':
        tname = 'LG_501'
    t = Tournament.objects.get(name=tname)
    return t


def _get_dt(d, t):
    date = datetime.strptime(d, "%Y-%m-%d").date()
    time = datetime.strptime(t, "%H:%M").time()
    dt = datetime.combine(date, time)
    dt = dt.replace(tzinfo=ZoneInfo('Canada/Eastern'))
    return dt


def ranking(scores):
    """
    scores is a list of the score such as:['33', '44', '55']
    Return the respective ranks of the score: [3, 2, 1]
    """
    result = []
    sorted = list(scores)
    sorted.sort(reverse=True)

    [result.append(sorted.index(s)+1) for s in scores]
    return result


def create_darts(d_dict, u):
    try:
        for d in d_dict:
            q = Darts.objects.filter(name=d)
            if not q:
                darts = Darts(
                    name=d,
                    user=u,
                    weight=d_dict[d]['weight'],
                    description=d_dict[d]['description'],
                    active=True
                )
                darts.save()
    except:
        return False
    return True


def create_tournaments(t_dict, darts, u):
    date = datetime.strptime('2007-01-01', "%Y-%m-%d").date()
    try:
        for t in t_dict:
            gt = GameType.objects.get(name=t_dict[t])
            tournament = Tournament(
                name=t,
                gametype=gt,
                scheduling='Continual',
                matching='all',
                start_date=date,
                end_date=None,
                active=True,
                editable=True,
                city='Québec/Deux-Montagnes',
                country='Canada',
                user=u
                )
            tournament.save()
            for d in darts:
                tournament.darts.add(d)
            tournament.save()
    except:
        return False
    return True


def main():
    """
        The players PP HH22 and HH18 will be created in the db and should not already exist
        The tournaments 'LG_BB' and 'LG_501' be created in the db and should not already exist
    """
    print('startinng...')
    fnBB = 'scripts/BBScores.csv'
    fn501 = 'scripts/501_.csv'
    files = [fnBB, fn501]
    u = User.objects.get(username='luc')
    t_dict = {
        'LG_BB': 'BB',
        'LG_501': '501'
    }
    d_dict = {
        'PP': {
            'weight': 25,
            'description': 'Harrows Power Point 80% Tungsten Steel Tip Darts'
        },
        'HH22': {
            'weight': 22,
            'description': 'Bottelsen Hammer Head No Bounce Steel Tip Darts'
        },
        'HH18': {
            'weight': 18,
            'description': 'Bottelsen Precision Grip Hammer Head Convertible Black Steel Darts'
        }
    }
    dnames = [d for d in d_dict]
    if create_darts(d_dict=d_dict, u=u):
        darts = Darts.objects.filter(name__in=dnames)
        if create_tournaments(t_dict=t_dict, darts=darts, u=u):
            for f in files:
                if not csv_to_db(f, darts):
                    print('Error entering games in the db')
                    break
                else:
                    print('It worked!')
        else:
            print('Error creating the tournaments')
    else:
        print('Error creating the darts')


if __name__ == "__main__":
    print('starting...')
main()

from .forms import RRParticipantForm, RRGameForm

import pandas as pd
import csv
import io


def rankstable(games, tournament):
    """
    :param games: queryset of games.Games
    :param tournament: games.Tournament object
    :return:
    main_headers
    ['#', 'Date', 'Time', '1', '2', '3', '']
    main_tbl
    {12: [5, '2022-08-20', '03:58', 'ddd', 'aaa+ccc', '', 12], 11: [4, '2022-08-20', '03:57', 'ddd', 'ccc', 'aaa', 11],
     10: [3, '2022-08-20', '03:57', 'ccc+ddd', '', 'aaa', 10], 9: [2, '2022-08-20', '03:56', 'ccc', 'aaa', 'ddd', 9],
     8: [1, '2022-08-20', '03:56', 'aaa', 'ccc', 'ddd', 8]}
    summary_headers
    ['Name', '1', '2', '3', 'pts']
    summary_tbl
    [['ccc', 2, 3, 0, 12], ['ddd', 3, 0, 2, 11], ['aaa', 1, 2, 2, 9]]
    """
    darts = tournament.darts.all()
    main_tbl = {}
    rankdict = {d.name: [] for d in darts}
    maxplist = [str(i) for i in range(1, len(darts) + 1)]
    main_headers = ['#', 'Date', 'Time'] + maxplist + ['']
    ngames = len(games)
    for idx, game in enumerate(games):
        dlocal = game.get_datetime
        main_tbl[game.id] = [ngames-idx,
               dlocal.strftime("%Y-%m-%d"),
               dlocal.strftime("%H:%M")] + game.get_ranking()
        for d in game.participant_set.all():
            rankdict[d.darts.name].append(d.rank)
    summary_headers, summary_tbl = _summary_table_new(rankdict, maxplist)
    return main_headers, main_tbl, summary_headers, summary_tbl


def _summary_table_new(t, maxplist):
    '''
        -t is a dict giving the position (ranks) of the player in each game
        and the total points for all players such as
        {'PP':  [2, 2, ... 2]},
         'HH22': [1, 1,... 1],},
          'HH18': [3, 3, ... 3]}}
        -maxplist is a list with n number according to the number of participants in the tournament ['1','2',...]
        This function creates a summary table and the output will be a list of list such as:
            [[PP, 	41,	31,	32,	217],
            [HH22,	37,	31,	36,	209],
            [HH18,	29,	43,	32,	205]]
    '''
    nranks = len(t)
    scorerange = range(1, nranks + 1)
    result = []
    for dart, ranks in t.items():
        row = [dart]
        total = 0
        nr = nranks
        for r in scorerange:
            x = ranks.count(r)
            row.append(x)
            total += x * nr
            nr -= 1
        row.append(total)
        result.append(row)
    result.sort(key=lambda x: x[len(t) + 1], reverse=True)
    stheader = ['Name'] + maxplist + ['pts']
    return stheader, result


def bb_score_tables(games, tournament):
    """
    :param games: queryset of games.Games
    :param tournament: games.Tournament object
    :return:
    main_headers
    ['#', 'Date', 'Time', '1', '2', '3', '']
    main_tbl
    {16: [7, '2022-08-27', '02:47', 44, 34, 35, 37.67], 15: [6, '2022-08-27', '02:12', 34, 51, 45, 43.33],
    13: [5, '2022-08-26', '02:27', 46, 47, 36, 43.0]...}
     summary_headers
    ['Name', '1', '2', '3', 'pts']
    summary_tbl
    [['ccc', 2, 3, 0, 12], ['ddd', 3, 0, 2, 11], ['aaa', 1, 2, 2, 9]]
    """
    darts = tournament.darts.all()
    tbb = {}
    alldarts = []
    scores_tbl = {}
    for d in darts:
        name = d.name
        alldarts.append(name)
        scores_tbl[name] = []
    ngames = len(games)
    for idx, game in enumerate(games):
        dlocal = game.get_datetime
        tbb[game.id] = [ngames - idx,
                        dlocal.strftime("%Y-%m-%d"),
                        dlocal.strftime("%H:%M")]
        for d in game.participant_set.all():
            scores_tbl[d.darts.name].append(d.score)
    df = pd.DataFrame(scores_tbl)
    summary_tbl = [['Mean'] + list(df.mean().round(decimals=2)), ['STDev'] + list(df.std(ddof=0).round(decimals=2))]
    df['mean'] = df.mean(axis=1).round(decimals=2)
    dftbb = pd.DataFrame(tbb).T
    df.index = dftbb.index
    ft = pd.concat([dftbb, df], axis=1)
    main_tbl = ft.T.to_dict('list')
    main_headers = ['#', 'Date', 'Time'] + list(df.columns) + ['']
    summary_headers = [' '] + alldarts
    return main_headers, main_tbl, summary_headers, summary_tbl


def write_csv(h1, l1, h2, l2):
    """
    write a csv file
        o = output file name
        h1-2 is a list with the table columns header
        l1-2 is a list of list of elements to display in the table
    """
    #
    # create csv in memory as StringIO
    #
    mem_file = io.StringIO()
    csv_writer = csv.writer(mem_file)
    csv_writer.writerow(h1)
    csv_writer.writerows(l1.values())
    csv_writer.writerows([''])
    csv_writer.writerow(h2)
    csv_writer.writerows(l2)
    csv_writer.writerows([''])
    mem_file.seek(0)
    return mem_file


def round_robin_formset(tournament):
    """
    :param tournament:
    :return:
    """
    games = tournament.game_set.all().order_by('round', '-datetime')
    gametype = tournament.gametype.name
    p_ranks = {}
    p_scores = {}
    formset_dict = {}
    for round in range(1, tournament.number_of_rounds + 1):
        formset_dict[round] = [f"Round {round}"]
        roundgames = games.filter(round=round)
        for g in roundgames:
            formset_dict[g.id] = [RRGameForm(instance=g)]
            if g.played:
                dlocal = g.get_datetime
                formset_dict[g.id].append(dlocal.strftime("%Y-%m-%d"))
                formset_dict[g.id].append(dlocal.strftime("%H:%M"))
                scores = g.get_scores()
                ranks = g.get_ranks()
                for p in ranks:
                    p_ranks.setdefault(p, []).append(ranks[p])
                    if gametype != '501':
                        p_scores.setdefault(p, []).append(scores[p])
            else:
                formset_dict[g.id].append('__')
                formset_dict[g.id].append('__')

            for p in g.participant_set.all():
                formset_dict[g.id].append(p.darts.name)
                f = RRParticipantForm(instance=p, game_type=gametype)
                formset_dict[g.id].append(f)
            formset_dict[g.id].append(g.played)
    print(formset_dict)
    standings_tbl = rr_standings(p_ranks, p_scores, gametype)
    standings_headers = ['W', 'L', 'D', 'pts']
    if gametype != '501':
        standings_headers.append('ppg')

    return formset_dict, standings_headers, standings_tbl


def rr_standings(p_ranks, p_scores, gametype ):
    standings = []
    for p in p_ranks:
        d = frequencyDistribution(p_ranks[p])
        temp = [p] + [d.get(n, 0) for n in [2, 0, 1]]
        temp.append(sum(p_ranks[p]))
        if gametype != '501':
            temp.append(average(p_scores[p]))
        standings.append(temp)
    return standings


def frequencyDistribution(data):
    return {i: data.count(i) for i in data}


def average(lst):
    return round(sum(lst) / len(lst), 1)

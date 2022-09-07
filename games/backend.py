import pandas as pd

from games.models import Game, Tournament, Darts, Participant

def create_balanced_round_robin(players, nrr, byelble="bye", roundlbl="Round"):
    """
    Create a round-robin schedule for the players
    :param players: list of players
    :param nrr: number of round-robin complete rounds
    :param byelble: label for opponent in a bye. Can be None
    :param roundlbl: label for each round. The default is "round" will be rendered as Round-1, Round-2,...
    :return: dictionary
    """
    s = {}
    try:
        nrr = int(nrr)
    except ValueError:
        pass  # it was a string, not an int.

    if len(players) % 2 == 1: players = players + [byelble]
    # manipulate map (array of indexes for list) instead of list itself
    # this takes advantage of even/odd indexes to determine home vs. away
    n = len(players)
    map = list(range(n))
    mid = n // 2
    for i in range(n - 1):
        l1 = map[:mid]
        l2 = map[mid:]
        l2.reverse()
        round = []
        for j in range(mid):
            t1 = players[l1[j]]
            t2 = players[l2[j]]
            if j == 0 and i % 2 == 1:
                # flip the first match only, every other round
                # (this is because the first match always involves the last player in the list)
                round.append((t2, t1))
            else:
                round.append((t1, t2))
        iround = i + 1
        roundlable = f"{roundlbl}-{iround}"
        s[roundlable] = round
        # rotate list by n/2, leaving last element at the end
        map = map[mid:-1] + map[:mid] + map[-1:]

    snrr = s.copy()
    # add number of additional complete rounds
    for j in range(1, nrr):
        for r in s:
            iround += 1
            roundlable = f"{roundlbl}-{iround}"
            if j % 2:
                temp = []
                for g in s[r]:
                    temp.append(tuple(reversed(g)))
                snrr[roundlable] = temp
            else:
                snrr[roundlable] = s[r]
    return snrr



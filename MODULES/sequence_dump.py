import pandas as pd
import numpy as np

# global variable for all possible play types
SEQUENCES = ["Spot-Up", "Transition", "Post-Up", "P&R Ball Handler", "Cut", "Hand Off", "Offensive Rebound", "Off Screen", "ISO", "P&R Roll Man", "Miscellaneous"]

def parse_play(play_list, tallies):
    play_list = [play.strip() for play in play_list]
    for event in play_list:
        if event == 'Miss 2 Pts' or event == 'Miss 3 Pts':
            tallies['attempts'] += 1
        if event == 'Miss 3 Pts':
            tallies['3PT attempts'] += 1
        if event == 'Make 2 Pts' or event == 'Make 3 Pts':
            tallies['makes'] += 1
            tallies['attempts'] += 1
            if event == 'Make 2 Pts':
                tallies['points'] += 2
            elif event == 'Make 3 Pts':
                tallies['points'] += 3
                tallies['3PT makes'] += 1
                tallies['3PT attempts'] += 1
        if event == 'Guarded':
            tallies['guarded'] += 1
        if event == 'Open':
            tallies['open'] += 1
        if event == 'Turnover':
            tallies['turnovers'] += 1
        if event == 'Free Throw':
            tallies['points'] += 1
            tallies['FT attempts'] += 1
        if event == 'Made':
            tallies['points'] += 1
            tallies['FT makes'] += 1
    tallies['possessions'] += 1
    return tallies

def tally_stats(plays):
    tallies = {'attempts': 0, 'makes': 0, 'guarded': 0, 'open': 0, '3PT attempts': 0, '3PT makes': 0, 'turnovers': 0, 'possessions': 0, 'FT attempts': 0, 'FT makes': 0, 'points': 0}
    for play in plays:
        tallies = parse_play(play, tallies)
    return tallies

def compute_stats(tallies, game_count):
    # print(tallies)
    stats = {}
    stats['Plays/Game'] = tallies['possessions'] / game_count
    stats['Points'] = tallies['points'] / game_count
    stats['PPP'] = tallies['points'] / tallies['possessions'] if tallies['possessions'] != 0 else np.nan
    stats['FGM'] = tallies['makes'] / game_count
    stats['FGA'] = tallies['attempts'] / game_count
    stats['FG%'] = (stats['FGM'] / stats['FGA']) * 100 if stats['FGA'] != 0 else np.nan
    # https://thesaucereport.wordpress.com/2009/04/28/adjusted-field-goal-percentage/
    stats['aFG%'] = ((stats['Points'] - (tallies['FT makes'] / game_count)) / (2 * stats['FGA'])) * 100 if stats['FGA'] != 0 else np.nan
    stats['TO%'] = (tallies['turnovers'] / tallies['possessions']) * 100 if tallies['possessions'] != 0 else np.nan
    stats['FT%'] = (tallies['FT makes'] / tallies['FT attempts']) * 100 if tallies['FT attempts'] != 0 else np.nan
    return stats

def get_stats_dict(input_dict, games):
    # Calculate overall stats for play type  
    stat_dict = {}
    for key in input_dict.keys():
        tallies = tally_stats(input_dict[key])
        stat_dict[key] = compute_stats(tallies, len(games))
        # print(key, tallies)
    return stat_dict

def get_plays_dict(games, team):
    plays_dict = {seq: [] for seq in SEQUENCES}
    for game in games:
        for poss in game:
            if poss["team"] == team:
                sequence = poss["plays"]

                # get a list of all indices at which each keyword play happens
                play_indices = []
                for idx, event in enumerate(sequence):
                    if event in SEQUENCES:
                        # found a play
                        play_indices.append(idx)

                if len(play_indices) == 0:
                    continue
                elif len(play_indices) == 1:
                    plays_dict[sequence[play_indices[0]]].append(sequence)
                else:
                    prev_idx = play_indices[0]
                    for play_idx in play_indices[1:]:
                        subplay = sequence[prev_idx-1:play_idx-1]
                        plays_dict[subplay[1]].append(subplay)
                        prev_idx = play_idx
                    subplay = sequence[play_idx-1:]
                    plays_dict[subplay[1]].append(subplay)
    return plays_dict

def run_analytics(games, team):
    # {spot up: [play 1, play 2, ...], post up: [play 1, play 2, ...], ...}
    plays_dict = get_plays_dict(games, team)
    play_type_dict = get_stats_dict(plays_dict, games)
    play_type_df = pd.DataFrame.from_dict(play_type_dict, orient='index').dropna(subset=['FG%']).round(2)

    # {25 Fru Che: [play 1, play 2, ...], 3 Devonn Allen: [play 1, play 2, ...], ...}
    player_dict = get_player_dict(plays_dict)

    # {25 Fru Che: {'Plays/Game': 19.333, 'Points': 14.0, 'PPP': 0.72, ...}, 3 Devonn Allen: {...}, ...}
    player_stat_dict = get_stats_dict(player_dict, games)
    print(player_stat_dict)
    player_stat_df = pd.DataFrame.from_dict(player_stat_dict, orient='index').round(2)

    player_play_dict = get_player_play_dict(player_dict)

    return plays_dict, play_type_df, play_type_dict, player_stat_df

def get_player_dict(plays_dict):
    player_dict = {}
    for pt in plays_dict.keys():
        for sequence in plays_dict[pt]:
            player = sequence[0]
            # verify it is a player if token that starts with jersey number
            if player.split(' ')[0].isdigit() and player[2:5] != 'Pts':
                if player not in player_dict.keys():
                    player_dict[player] = []
                player_dict[player].append(sequence)
            else:
                continue
    return player_dict

def get_player_play_dict(player_dict):
    player_play_dict = {player: {seq: [] for seq in SEQUENCES} for player in player_dict}
    for player in player_dict:
        plays = player_dict[player]
        for seq in SEQUENCES:
            # print("--------  " + seq)
            for play in plays:
                if play[1] == seq:
                    # print(play)
                    player_play_dict[player][seq].append(play)
    return player_play_dict

def get_hierarchical_plays(play_types, plays_dict):
    output = []
    for pt in play_types:
        for sequence in plays_dict[pt]:
            if sequence[1] == pt:
                output.append(sequence[1:5])
    df = pd.DataFrame(output, columns=['A', 'B', 'C', 'D'])
    print(df.head())
    return df

def print_dict(d):
    for key in d.keys():
        print(key)
        print(d[key])
        print()
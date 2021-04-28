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

def tally_player_stats(plays):
    tallies = {'attempts': 0, 'makes': 0, 'guarded': 0, 'open': 0, '3PT attempts': 0, '3PT makes': 0, 'turnovers': 0, 'possessions': 0, 'FT attempts': 0, 'FT makes': 0, 'points': 0}
    for play in plays:
        tallies = parse_play(play, tallies)
    return tallies

def compute_stats(tallies, game_count):
    stats = {}
    stats['Plays/Game'] = tallies['possessions'] / game_count
    stats['Points'] = tallies['points'] / game_count
    stats['PPP'] = tallies['points'] / tallies['possessions'] if tallies['possessions'] != 0 else np.nan
    stats['FGM'] = tallies['makes'] / game_count
    stats['FGA'] = tallies['attempts'] / game_count
    stats['FG%'] = (stats['FGM'] / stats['FGA']) * 100 if stats['FGA'] != 0 else np.nan
    # https://thesaucereport.wordpress.com/2009/04/28/adjusted-field-goal-percentage/
    stats['aFG%'] = ((stats['Points'] - tallies['FT makes']) / (2 * stats['FGA'])) * 100 if stats['FGA'] != 0 else np.nan
    stats['TO%'] = (tallies['turnovers'] / tallies['possessions']) * 100 if tallies['possessions'] != 0 else np.nan
    stats['FT%'] = (tallies['FT makes'] / tallies['FT attempts']) * 100 if tallies['FT attempts'] != 0 else np.nan
    print(stats)
    return stats

def get_stats_dict(plays_dict, games):
    # Calculate overall stats for play type  
    stat_dict = {}
    for seq in SEQUENCES:
        tallies = tally_stats(plays_dict[seq])
        stat_dict[seq] = compute_stats(tallies, len(games))
    return stat_dict

def run_analytics(games, team):
    plays_dict = {seq: [] for seq in SEQUENCES}
    full_seq = True
    output = []
    for game in games:
        for poss in game:
            if poss["team"] == team:
                plays = poss["plays"]

                play_indices = []
                for idx, play in enumerate(plays):
                    if play in SEQUENCES:
                        # found a play
                        play_indices.append(idx)

                # plays_dict[plays[repeat]].append(repeat_output)
                # loop up to each one and store in player dict
                for idx, play_idx in enumerate(play_indices):
                    player = plays[play_idx - 1]

                    if plays[play_idx] in SEQUENCES:
                        if idx < len(play_indices) - 1:
                            subplays = []
                            for play_id in range (play_idx, play_indices[idx+1]-1):
                                subplays.append(plays[play_id])
                            # at corresponding sequence, append subplay list
                            plays_dict[plays[play_idx]].append(subplays)
                        elif idx == 0 and len(play_indices) == 1:
                            plays_dict[plays[play_idx]].append(plays)
                        else:
                            # taking from the player within the play to the end
                            subplays = []
                            for idx in range (play_idx, len(plays)):
                                subplays.append(plays[idx])
                            plays_dict[subplays[0]].append(subplays)

    
    stat_dict = get_stats_dict(plays_dict, games)
        
    stat_df = pd.DataFrame.from_dict(stat_dict, orient='index').dropna(subset=['FG%'])
    player_stats, player_play_dict = get_player_stats(games, team)
   
    # print("\n\n Return player_play_dict for following\n Player & play dict for Fru Che",player_play_dict['25 Fru Che']['Spot-Up'])
    return stat_df, stat_dict, player_stats

def get_player_stats(games, team):
    player_dict = {}
    full_seq = True
    for game in games:
        for poss in game:
            if poss["team"] == team:
                plays = poss["plays"]
                player_indices = []
                # split on any token that starts with number
                # keep list of repeat players
                for idx, play in enumerate(plays):
                    if play.split(' ')[0].isdigit() and play[2:5] != 'Pts':
                        # found a player
                        player_indices.append(idx)
                # loop up to each one and store in player dict
                for idx, player_idx in enumerate(player_indices):
                    player = plays[player_idx]
                    if plays[player_idx + 1] in SEQUENCES:
                        if player not in player_dict:
                            player_dict[player] = []

                        # if the play is in sequnces
                        if idx < len(player_indices) - 1:
                            subplays = []
                            for play_idx in range (player_idx, player_indices[idx+1]+1):
                                subplays.append(plays[play_idx])
                            player_dict[subplays[0]].append(subplays)
                        elif idx == 0 and len(player_indices) == 1:
                            player_dict[plays[0]].append(plays)
                        else:
                            # taking from the player within the play to the end
                            subplays = []
                            for play_idx in range (player_idx, len(plays)):
                                subplays.append(plays[play_idx])
                            player_dict[subplays[0]].append(subplays)

    player_stat_dict = {}
    for player in player_dict.keys():
        tallies = tally_player_stats(player_dict[player])
        player_stat_dict[player] = compute_stats(tallies, len(games))
    player_stat_df = pd.DataFrame.from_dict(player_stat_dict, orient='index')

    player_play_dict = get_player_play_dict(player_dict)
    return player_stat_df, player_play_dict

def get_player_play_dict(player_dict):
    player_play_dict = {}
    for player in player_dict:
        player_play_dict[player] = {}
        for seq in SEQUENCES:
            player_play_dict[player][seq] = []

    for player in player_dict:
        plays = player_dict[player]
        for seq in SEQUENCES:
            for play in plays:
                if play[1] == seq:
                    player_play_dict[player][seq].append(play)
    return player_play_dict

def get_hierarchical_plays(games, team, sequences):
    output = []
    full_seq = False
    for seq in sequences:
        for game in games:
            for poss in game:
                if poss["team"] == team:
                    plays = poss["plays"]
                    for index in range(len(plays)):
                        player = plays[0]
                        match = True
                        
                        # index+1 is the play type, index is just the player
                        if plays[index+1] != seq:
                            match = False
                            break
                        
                        if match:
                            flag = True
                            play_seq = ""
                            for match_index in range(1, len(plays)):
                                if plays[match_index] in sequences and plays[match_index] != seq:
                                    flag = False
                                if plays[match_index] == seq:
                                    flag = True
                                if flag:
                                    play_seq += "{} > ".format(plays[match_index])
                                else:
                                    continue
                                
                            # play_seq = play_seq[0:len(play_seq) - 2]
                            output.append(play_seq.split(" > ")[:4])
                            break
    df = pd.DataFrame(output, columns=['A', 'B', 'C', 'D'])
    return df

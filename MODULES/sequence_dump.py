import pandas as pd
import numpy as np

def round_nums(x):
    try:
        return round(x, 2)
    except:
        return x

def parse_play(play_list, tallies):
    seq = play_list.split(' > ')
    seq = [info.strip() for info in seq]
    for event in seq:
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

def parse_player_only_play(play_list, tallies):
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
        print(play)
        if isinstance(play, list):
            for poss in play:
                tallies = parse_play(poss, tallies)
        else:
            tallies = parse_play(play, tallies)
    return tallies

def tally_player_stats(plays):
    tallies = {'attempts': 0, 'makes': 0, 'guarded': 0, 'open': 0, '3PT attempts': 0, '3PT makes': 0, 'turnovers': 0, 'possessions': 0, 'FT attempts': 0, 'FT makes': 0, 'points': 0}
    for play in plays:
        if isinstance(plays, list):
            play = [val.strip() for val in play]
            tallies = parse_player_only_play(play, tallies)
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


def run_analytics(games, team):
    sequences = ["Spot-Up", "Transition", "Post-Up", "P&R Ball Handler", "Cut", "Hand Off", "Offensive Rebound", "Off Screen", "ISO", "P&R Roll Man", "Miscellaneous"]

    plays_dict = {seq: [] for seq in sequences}
    full_seq = True
    for seq in sequences:
        output = []
        for game in games:
            for poss in game:
                if poss["team"] == team:
                    plays = poss["plays"]

                    repeat_indices = []
                    # Get all instances of more play types within a possession
                    # Example: ['33 Eric Sellew', 'Non Shooting Foul', '3 Devonn Allen', 'Cut', 'Basket', 'Make 2 Pts']
                    # Split at Devonn Allen, store that index in repeat_indices
                    for idx, play in enumerate(plays):
                        if play in sequences and idx > 1:
                            repeat_indices.append(idx)

                    # Parse through those repeats
                    repeat_output = ""
                    for idx, repeat in enumerate(repeat_indices):
                        # Grab player name to store in the player dict
                        player = plays[repeat - 1]

                        if idx < len(repeat_indices) - 1:
                            repeat_output = plays[repeat-1] + " > "
                            for r in range(repeat, repeat_indices[idx + 1]-1):
                                repeat_output += "{} > ".format(plays[r])
                            repeat_output = repeat_output[0:len(repeat_output) - 2]

                            # Store the subplays under the corresponding play type
                            plays_dict[plays[repeat]].append(repeat_output)

                        else:
                            # If we are at the second to last repeat index of repeat indices,
                            # need to store everything up to the end of that play 
                            repeat_output = plays[repeat_indices[idx]-1]  + " > "
                            for r in range(repeat_indices[idx], len(plays)):
                                repeat_output += "{} > ".format(plays[r])

                            # Store the subplays under the corresponding play type
                            repeat_output = repeat_output[0:len(repeat_output) - 2]
                            plays_dict[plays[repeat]].append(repeat_output)
                    for index in range(len(plays)):
                        player = plays[0]

                        match = True
                        # index+1 is the play type, index is just the player
                        # if the play does not contain the proper sequence, don't store
                        if plays[index+1] != seq:
                            match = False
                            break
                        
                        if match:
                            play_seq = ""
                            if full_seq:
                                for match_index in range(0, len(plays)):
                                    play_seq += "{} > ".format(plays[match_index])
                                play_seq = play_seq[0:len(play_seq) - 2]
                            output.append(play_seq)
                            break

        
        # Add subplays to the play dict at that play type
        plays_dict[seq].append(output)    

    # Calculate overall stats for play type  
    stat_dict = {}
    for seq in sequences:
        tallies = tally_stats(plays_dict[seq])
        stat_dict[seq] = compute_stats(tallies, len(games))
    stat_df = pd.DataFrame.from_dict(stat_dict, orient='index')

    player_stats, player_play_dict = get_player_stats(games, team)
   
    # print("\n\n Return player_play_dict for following\n Player & play dict for Fru Che",player_play_dict['25 Fru Che']['Spot-Up'])
    return stat_df, player_stats

def get_player_stats(games, team):
    sequences = ["Spot-Up", "Transition", "Post-Up", "P&R Ball Handler", "Cut", "Hand Off", "Offensive Rebound", "Off Screen", "ISO", "P&R Roll Man", "Miscellaneous", "Free Throw"] 
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
                    if plays[player_idx + 1] in sequences:
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

    # take care of rounding
    for col in player_stat_df.columns:
        player_stat_df[col] = player_stat_df[col].apply(lambda x: round_nums(x))

    player_play_dict = get_player_play_dict(player_dict)
    return player_stat_df, player_play_dict

def get_player_play_dict(player_dict):
    sequences = ["Spot-Up", "Transition", "Post-Up", "P&R Ball Handler", "Cut", "Hand Off", "Offensive Rebound", "Off Screen", "ISO", "P&R Roll Man", "Miscellaneous"]
    player_play_dict = {}
    for player in player_dict:
        player_play_dict[player] = {}
        for seq in sequences:
            player_play_dict[player][seq] = []

    for player in player_dict:
        plays = player_dict[player]
        for seq in sequences:
            for play in plays:
                if play[1] == seq:
                    player_play_dict[player][seq].append(play)
    return player_play_dict

def get_hierarchical_plays(games, team):
    sequences = ["Spot-Up", "Transition", "Post-Up", "P&R Ball Handler", "Cut", "Hand Off", "Offensive Rebound", "Off Screen", "ISO", "P&R Roll Man", "Miscellaneous"]
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

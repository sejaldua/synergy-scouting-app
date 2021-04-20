import pandas as pd

def round_nums(x):
    if x == "N/A":
        return x
    return round(x, 2)

def tally_stats(plays):
    tallies = {'attempts': 0, 'makes': 0, 'guarded': 0, 'open': 0, '3PT attempts': 0, '3PT makes': 0, 'turnovers': 0, 'possessions': 0, 'FT attempts': 0, 'FT makes': 0, 'points': 0}
    
    for play in plays:
        play_str = ""
        if isinstance(play, list):
            for poss in play:
                # Counting repeats 
                tallies['possessions'] += 1
                play_str += " > " + poss
            print(play_str)
            play = play_str

        seq = play.split(' > ')
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
    print(tallies)
    return tallies

def compute_stats(tallies, game_count):
    stats = {}
    stats['poss/game'] = tallies['possessions'] / game_count
    stats['points'] = tallies['points'] / game_count

    stats['PPP'] = tallies['points'] / tallies['possessions'] if tallies['possessions'] != 0 else "N/A"
    stats['FGM'] = tallies['makes'] / game_count
    stats['FGA'] = tallies['attempts'] / game_count
    stats['FG%'] = (stats['FGM'] / stats['FGA']) * 100 if stats['FGA'] != 0 else "N/A"
    # https://thesaucereport.wordpress.com/2009/04/28/adjusted-field-goal-percentage/
    stats['aFG%'] = ((stats['points'] - stats['FGM']) / (2 * stats['FGA'])) * 100 if stats['FGA'] != 0 else "N/A"
    stats['%TO'] = (tallies['turnovers'] / tallies['possessions']) * 100 if tallies['possessions'] != 0 else "N/A"
    stats['%FT'] = (tallies['FT makes'] / tallies['FT attempts']) * 100 if tallies['FT attempts'] != 0 else "N/A"
    print(stats)
    return stats


def run_analytics(games, team):
    sequences = ["Spot-Up", "Transition", "Post-Up", "P&R Ball Handler", "Cut", "Hand Off", "Offensive Rebounds", "Off Screen", "ISO", "P&R Roll Man", "Miscellaneous"]

    plays_dict = {seq: [] for seq in sequences}
    full_seq = True
    for seq in sequences:
        output = []
        for game in games:
            for poss in game:
                if poss["team"] == team:
                    plays = poss["plays"]
                    
                    repeat_indices = []
                    repeat_output = ""
                    for idx, play in enumerate(plays):
                        if play in sequences and idx > 1:
                            repeat_indices.append(idx)

                    for idx, repeat in enumerate(repeat_indices):
                        if idx < len(repeat_indices) - 1:
                            repeat_output = ""
                            for r in range(repeat_indices[idx], repeat_indices[idx + 1]):
                                repeat_output += "{} > ".format(plays[r])
                                
                            repeat_output = repeat_output[0:len(repeat_output) - 2]
                            plays_dict[plays[repeat]].append(repeat_output)

                        else:
                            repeat_output = ""
                            for r in range(repeat_indices[idx], len(plays)):
                                repeat_output += "{} > ".format(plays[r])
                                
                            repeat_output = repeat_output[0:len(repeat_output) - 2]
                            plays_dict[plays[repeat]].append(repeat_output)

                    for index in range(len(plays)):
                        player = plays[0]
                        match = True
                        
                        # index+1 is the play type, index is just the player
                        if plays[index+1] != seq:
                            match = False
                            break
                        
                        if match:
                            play_seq = ""
                            if full_seq:
                                for match_index in range(0, len(plays)):
                                    play_seq += "{} > ".format(plays[match_index])
                                
                                play_seq = play_seq[0:len(play_seq) - 2]
                            else:
                                for match_index in range(index, len(plays)):
                                    play_seq += "{} > ".format(plays[match_index])
                                
                                play_seq = play_seq[0:len(play_seq) - 2]
                            
                            output.append(play_seq)
                            break

        plays_dict[seq].append(output)      
                   
    stat_dict = {}
    for seq in sequences:
        print(seq)
        tallies = tally_stats(plays_dict[seq])
        stat_dict[seq] = compute_stats(tallies, len(games))
    df = pd.DataFrame.from_dict(stat_dict, orient='index')

    # take care of rounding
    for col in df.columns:
        df[col] = df[col].apply(lambda x: round_nums(x))
    print(df)
    return df

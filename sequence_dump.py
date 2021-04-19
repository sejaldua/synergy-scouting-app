import operator
import streamlit as st


def tally_stats(plays):
    tallies = {'attempts': 0, 'makes': 0, 'guarded': 0, 'open': 0, '3PT attempts': 0, '3PT makes': 0, 'turnovers': 0, 'possessions': 0, 'FT attempts': 0, 'FT makes': 0, 'points': 0}
    for play in plays:
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
    stats['PPP'] = tallies['points'] / tallies['possessions']
    stats['FGM'] = tallies['makes'] / game_count
    stats['FGA'] = tallies['attempts'] / game_count
    stats['FG%'] = (stats['FGM'] / stats['FGA']) * 100
    # https://thesaucereport.wordpress.com/2009/04/28/adjusted-field-goal-percentage/
    stats['aFG%'] = ((stats['points'] - tallies['FT makes']) / (2 * stats['FGA'])) * 100
    stats['%TO'] = (tallies['turnovers'] / tallies['possessions']) * 100
    stats['%FT'] = (tallies['FT attempts'] / tallies['FT makes']) * 100
    print(stats)
    return stats


def run_analytics(games, team):
    print(len(games))
    sequences = ["Spot-Up", "Transition", "Post-Up", "P&R Ball Handler", "Cut", "Hand Off", "Offensive Rebounds", "Off Screen", "ISO", "P&R Roll Man", "Miscellaneous"]
    sequences = ["Post-Up", "Spot-Up"]
        
    full_seq = True
    output = []
    plays_dict = {}
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
                            
        plays_dict[seq] = output
    print(plays_dict)
    tallies = tally_stats(plays_dict['Post-Up'])
    compute_stats(tallies, len(games))
    return plays_dict

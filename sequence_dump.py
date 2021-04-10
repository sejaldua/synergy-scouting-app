import operator
import streamlit as st

def run_analytics(games, team):
    # print()
    # print("in sequence dump")
    # print()
    full_seq = True
    sequence_1 = ["Spot-Up", "No Dribble Jumper"]
    output = []
    for game in games:
        for poss in game:
            if poss["team"] == team:
                plays = poss["plays"]
                
                for index in range(0, len(plays)):
                    match = True
                    
                    for seq_index in range(0, len(sequence_1)):
                        if index + seq_index >= len(plays):
                            match = False
                            break
                            
                        if plays[index + seq_index] != sequence_1[seq_index]:
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
    return output

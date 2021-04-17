import operator
import streamlit as st


def run_analytics(games, team):
    sequences = ["Spot-Up", "Transition", "Post-Up", "P&R Ball Handler", "Cut", "Hand Off", "Hand Off", "Offensive Rebounds",\
        "Off Screen", "Isolation", "P&R Roll Man", "Miscellaneous"]
    sequences=["ISO"]
    full_seq = True
    output = []
    plays_dict = {}
    for seq in sequences:
        for game in games:
            for poss in game:
                if poss["team"] == team:
                    plays = poss["plays"]
                    print("plays are", plays)
                    
                    for index in range(0, len(plays)):
                        print(plays[index])
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
    # print(plays_dict)
    print(plays_dict["Cut"])
    return plays_dict

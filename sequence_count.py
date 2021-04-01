import operator

def run_analytics(games, team):
    sequence = ["24 Jack Farrell", "Transition", "Turnover"]
    count = 0
    
    for game in games:
        for poss in game:
            if poss["team"] == team:
                plays = poss["plays"]
                
                for index in range(0, len(plays)):
                    match = True
                    
                    for seq_index in range(0, len(sequence)):
                        if index + seq_index >= len(plays):
                            match = False
                            break
                            
                        if plays[index + seq_index] != sequence[seq_index]:
                            match = False
                            break
                            
                    if match:
                        count += 1
                        break
    
    print(" > ".join(sequence))
    print("Total: {}".format(count))
                    
        
                            
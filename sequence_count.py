import operator

# team stats
# opponent stats - other team spotted up for a shot (averaged for all opponents user checked)
# one dictionary for each player on the team
# team stats is big dictionary - for each player on amherst, they have a player dictionary within player dicitonary 

#noah and sook-hee - team breakdown, player info
#sejal doing oponents - step that lets user select subset of opponents, in run analytics what do we need to do to only focus on those games

def run_analytics(games, team):
    sequence = ["Spot-Up"]
    count = 0
    print("Hebbit", team)
    player_dict = {}
    for game in games:
        for poss in game:
            if poss["team"] == team:
                plays = poss["plays"]
                # split any plays that have sequence[0] multiple times to individual arrays
                # example: ['Spot-Up', 'No Dribble Jumper', 'Guarded', 'Long/3pt', 'Miss 3 Pts', '25 Fru Che', \
                # 'Offensive Rebound', 'Short', 'Run Offense', '3 Devonn Allen', 'Spot-Up', 'No Dribble Jumper', 'Guarded', 'Long/3pt', 'Miss 3 Pts']
                # should be split into two at each Spot-Up

                repeat_indices = []
                for idx, play in enumerate(plays):
                    
                    if play == sequence[0] and idx != 0:
                        # need to split the play
                        repeat_indices.append(idx)
                print("repeat indices", repeat_indices)
                for index in range(0, len(plays)):
                    # Elements will only start with a number if it is a player
                    # Example - 25 Fru Che
                    match = True
                    
                    for seq_index in range(0, len(sequence)):
                        if index + seq_index >= len(plays):
                            match = False
                            break
                          
                        if plays[index + seq_index] != sequence[seq_index]:
                            
                            match = False
                            break
                    

                    # Tally guarded/open, shot length [#num short, #num med, #num long]
                    if match:
                        print('plays', plays)
                        # print('play atindex is', plays[index-1])
                        player_plays = plays[index:]
                        # print('len of plays', len(plays), plays[index:])
                        # player_dict.add(plays[index-1], plays[index:]
                        count += 1
                        break
    # second value as the row, success or make, open or guarded
    # split on multiple spot ups/sequence at 0
    # get a spot up, go to sub-spotup in the dictionary, add 
    print(" > ".join(sequence))
    print("Total: {}".format(count))
                    
        
                            
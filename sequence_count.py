import operator

# team stats
# opponent stats - other team spotted up for a shot (averaged for all opponents user checked)
# one dictionary for each player on the team
# team stats is big dictionary - for each player on amherst, they have a player dictionary within player dicitonary 

#noah and sook-hee - team breakdown, player info
#sejal doing opponents - step that lets user select subset of opponents, in run analytics what do we need to do to only focus on those games

def run_analytics(games, team, sequence):
    count = 0
    play_dict = {}
    for game in games:
        for poss in game:
            if poss["team"] == team:
                plays = poss["plays"]
                # print(plays)
                # split any plays that have sequence[0] multiple times to individual arrays
                # example: ['Spot-Up', 'No Dribble Jumper', 'Guarded', 'Long/3pt', 'Miss 3 Pts', '25 Fru Che', \
                # 'Offensive Rebound', 'Short', 'Run Offense', '3 Devonn Allen', 'Spot-Up', 'No Dribble Jumper', 'Guarded', 'Long/3pt', 'Miss 3 Pts']
                # should be split into two at each Spot-Up
                repeat_indices = []
                for idx, play in enumerate(plays):
                    if play in sequence and idx != 0:
                        # need to split the play, record index for later
                        repeat_indices.append(idx)

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
                        if repeat_indices:
                            for i in range(len(repeat_indices)):
                                count += 1
                                if (plays[repeat_indices[i]+1] in play_dict):
                                    play_dict[plays[repeat_indices[i]+1]].append(plays[index+2:])
                                else:
                                    play_dict[plays[repeat_indices[i]+1]] = [plays[index+2:]]
                            break

                        else:        
                            if (plays[index+1] in play_dict):
                                play_dict[plays[index+1]].append(plays[index+2:])
                            else:
                                play_dict[plays[index+1]] = [plays[index+2:]]
                                
                            count += 1
                            break

    all_tally_dicts = {}
    for key in play_dict.keys():
        tallies = {
            "make": 0,
            "miss": 0,
            "guarded": 0,
            "open": 0,
        }

        for poss_plays in play_dict[key]:
            for play in poss_plays:
                if play == 'Guarded':
                    tallies['guarded'] = tallies['guarded'] + 1
                elif play == "Open":
                    tallies['open'] = tallies['open'] + 1
                elif play[:4] == 'Make':
                    tallies['make'] = tallies['make'] + 1
                elif play[:4] == 'Miss':
                    tallies['miss'] = tallies['miss'] + 1
        all_tally_dicts[key] = tallies

    print("All tally dicts for spot-up", all_tally_dicts)
    # split on multiple spot ups/sequence at 0
    print(" > ".join(sequence))
    print("Total: {}".format(count))
    return all_tally_dicts
                    
        
                            
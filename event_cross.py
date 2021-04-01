import operator

def calc_cross(plays, points, nopoints, total_points, total_nopoints):
    cross_plays = {}
    expected = total_points / total_nopoints
    
    for play in plays:
        # first row
        if play in points:
            in_points = points[play]
            exp_nopoints = (in_points * total_nopoints) / total_points
            
            if play in nopoints:
                cross_plays[play] = abs(exp_nopoints - nopoints[play])
            else: cross_plays[play] = exp_nopoints
        else: 
            in_nopoints = nopoints[play]
            exp_points = (in_nopoints * total_points) / total_nopoints
        
            cross_plays[play] = exp_points
        
        
    return cross_plays


def run_analytics(games, team):
    plays = []
    bi_plays = []
    tri_plays = []
    points = {}
    nopoints = {}
    bi_points = {}
    bi_nopoints = {}
    tri_points = {}
    tri_nopoints = {}
    total_points = 0
    total_nopoints = 0
    
    for game in games:
        for poss in game:
            if poss["team"] == team:
                this_poss = []
                
                if poss["points"] > 0:
                    total_points += 1
                    
                    for index in range(0, len(poss["plays"])):
                        play = poss["plays"][index]
                        
                        if play == "Made" or play == "Make 2 Pts" or play == "Make 3 Pts":
                            continue
                        if play == "Miss" or play == "Miss 2 Pts" or play == "Miss 3 Pts":
                            continue
                        
                        # single plays
                        if not play in plays:
                            plays.append(play)
                        
                        if play in points:
                            points[play] = points[play] + 1
                        else: points[play] = 1
                        
                        # play bi-grams
                        if index > 0:
                            prev_play = poss["plays"][index - 1]
                            bi_play = "{} > {}".format(prev_play, play)
                            
                            if not bi_play in bi_plays:
                                bi_plays.append(bi_play)
                            
                            if bi_play in bi_points:
                                bi_points[bi_play] = bi_points[bi_play] + 1
                            else: bi_points[bi_play] = 1
                        
                        # play tri-grams    
                        if index > 1:
                            prev_prev_play = poss["plays"][index - 2]
                            prev_play = poss["plays"][index - 1]
                            tri_play = "{} > {} > {}".format(prev_prev_play, prev_play, play)
                            
                            if not tri_play in tri_plays:
                                tri_plays.append(tri_play)
                            
                            if tri_play in tri_points:
                                tri_points[tri_play] = tri_points[tri_play] + 1
                            else: tri_points[tri_play] = 1
                else:
                    total_nopoints += 1
                    
                    for index in range(0, len(poss["plays"])):
                        play = poss["plays"][index]
                        
                        if play == "Made" or play == "Make 2 Pts" or play == "Make 3 Pts":
                            continue
                        if play == "Miss" or play == "Miss 2 Pts" or play == "Miss 3 Pts":
                            continue
                        
                        # single plays
                        if not play in plays:
                            plays.append(play)
                        
                        if play in nopoints:
                            nopoints[play] = nopoints[play] + 1
                        else: nopoints[play] = 1
                        
                        # play bi-grams
                        if index > 0:
                            prev_play = poss["plays"][index - 1]
                            bi_play = "{} > {}".format(prev_play, play)
                            
                            if not bi_play in bi_plays:
                                bi_plays.append(bi_play)
                            
                            if bi_play in bi_nopoints:
                                bi_nopoints[bi_play] = bi_nopoints[bi_play] + 1
                            else: bi_nopoints[bi_play] = 1
                        
                        # play tri-grams
                        if index > 1:
                            prev_prev_play = poss["plays"][index - 2]
                            prev_play = poss["plays"][index - 1]
                            tri_play = "{} > {} > {}".format(prev_prev_play, prev_play, play)
                            
                            if not tri_play in tri_plays:
                                tri_plays.append(tri_play)
                            
                            if tri_play in tri_nopoints:
                                tri_nopoints[tri_play] = tri_nopoints[tri_play] + 1
                            else: tri_nopoints[tri_play] = 1
                            
    
    # tri-plays
    cross_plays = calc_cross(tri_plays, tri_points, tri_nopoints, total_points, total_nopoints)
    
    sorted_cross = sorted(cross_plays.items(), key=lambda kv: kv[1], reverse=True)
    sorted_triplay = sorted(tri_points.items(), key=lambda kv: kv[1], reverse=True)
    
    print()
    print("Tri-Plays Points")
    count = 0
    for play in sorted_triplay:
        if count == 10:
            break
        count += 1
        
        if play[0] in tri_points:
            in_points = tri_points[play[0]]
        else: in_points = 0
        
        if play[0] in tri_nopoints:
            out_points = tri_nopoints[play[0]]
        else: out_points = 0
        
        print("{}    Points: {}, No Points: {}".format(play[0], in_points, out_points))
    
    print()
    print("Tri-Plays No Points")
    sorted_triplay = sorted(tri_nopoints.items(), key=lambda kv: kv[1], reverse=True)
    count = 0
    for play in sorted_triplay:
        if count == 10:
            break
        count += 1
        
        if play[0] in tri_points:
            in_points = tri_points[play[0]]
        else: in_points = 0
        
        if play[0] in tri_nopoints:
            out_points = tri_nopoints[play[0]]
        else: out_points = 0
        
        print("{}    Points: {}, No Points: {}".format(play[0], in_points, out_points))
        
    print()
    print("Tri-Plays Difference")
    count = 0
    for play in sorted_cross:
        if count == 10:
            break
        count += 1
        
        if play[0] in tri_points:
            in_points = tri_points[play[0]]
        else: in_points = 0
        
        if play[0] in tri_nopoints:
            out_points = tri_nopoints[play[0]]
        else: out_points = 0
        
        print("{}: {}    Points: {}, No Points: {}".format(play[0], round(play[1], 2), in_points, out_points))
        
    # bi-plays
    cross_plays = calc_cross(bi_plays, bi_points, bi_nopoints, total_points, total_nopoints)
    
    sorted_cross = sorted(cross_plays.items(), key=lambda kv: kv[1], reverse=True)
    sorted_biplay = sorted(bi_points.items(), key=lambda kv: kv[1], reverse=True)
    
    print()
    print("Bi-Plays Points")
    count = 0
    for play in sorted_biplay:
        if count == 10:
            break
        count += 1
        
        if play[0] in bi_points:
            in_points = bi_points[play[0]]
        else: in_points = 0
        
        if play[0] in bi_nopoints:
            out_points = bi_nopoints[play[0]]
        else: out_points = 0
        
        print("{}    Points: {}, No Points: {}".format(play[0], in_points, out_points))
        
    
    print()
    print("Bi-Plays No Points")
    sorted_biplay = sorted(bi_nopoints.items(), key=lambda kv: kv[1], reverse=True)
    count = 0
    for play in sorted_biplay:
        if count == 10:
            break
        count += 1
        
        if play[0] in bi_points:
            in_points = bi_points[play[0]]
        else: in_points = 0
        
        if play[0] in bi_nopoints:
            out_points = bi_nopoints[play[0]]
        else: out_points = 0
        
        print("{}    Points: {}, No Points: {}".format(play[0], in_points, out_points))
        
    print()
    print("Bi-Plays Difference")
    count = 0
    for play in sorted_cross:
        if count == 10:
            break
        count += 1
        
        if play[0] in bi_points:
            in_points = bi_points[play[0]]
        else: in_points = 0
        
        if play[0] in bi_nopoints:
            out_points = bi_nopoints[play[0]]
        else: out_points = 0
        
        print("{}: {}    Points: {}, No Points: {}".format(play[0], round(play[1], 2), in_points, out_points))
        
                            
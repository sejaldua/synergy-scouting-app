from __future__ import print_function
from html.parser import HTMLParser
from datetime import datetime, timedelta
from importlib import import_module
import re
import operator
import copy
from roster_images import get_player_headshots
import sys
import os
import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path

TEAMS_TO_SCOUT = ["amherst", "bates", "colby", "hamilton", "middlebury", "trinity"]
team_mappings = {"amherst": "AMH", "bates": "BAT", "colby": "COL", "hamilton": "HC", "middlebury": "MID", "trinity": "TCT"}
PLAY_TYPES = ["Spot-Up", "Transition", "Post-Up", "P&R Ball Handler", "Cut", "Hand Off", "Offensive Rebounds (put backs)", "Off Screen", "Isolation", "P&R Roll Man", "Miscellaneous"]

# Turn error messaging on (True), or off (False)
print_err = False
keep_row = False
raw_data = []
possessions = []


# Handler functions for the HTML parser
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': 
            global keep_row
            for name, value in attrs:
                if name == 'class' and value == 'PlayByPlayRow':
                    keep_row = True
                elif name == 'class' and value == 'PlayByPlayRowShaded':
                    keep_row = True
        else: return

    def handle_data(self, data):
        clean_data = data.strip()
        if len(clean_data) > 0:
            raw_data.append(clean_data)

# Convert the raw data from the HTML parser into a structured possession object        
def makePossession(raw_data):
    poss = {}
    poss["team"] = raw_data[0]
    poss["corrected"] = False
    poss["period"] = raw_data[1]
    poss["time"] = raw_data[2]
    poss["raw_plays"] = []
    
    end_range = len(raw_data)
    if raw_data[len(raw_data) - 2].strip() == "-":
        poss["score_1"] = int(raw_data[len(raw_data) - 3])
        poss["score_2"] = int(raw_data[len(raw_data) - 1])
        end_range = len(raw_data) - 3
    else:
        poss["score_1"] = 0
        poss["score_2"] = 0
    
    for index in range(3, end_range):
        poss["raw_plays"].append(raw_data[index])
        
    return poss

# Merge the provided possession with the previous one
def mergePossession(poss):
    prev_poss = possessions[len(possessions) - 1]
    prev_poss["time"] = poss["time"]
    prev_poss["score_1"] = poss["score_1"]
    prev_poss["score_2"] = poss["score_2"]
    
    for play in poss["raw_plays"]:
        prev_poss["raw_plays"].append(play)

# Add on to the previous play
def addPlay(play):
    prev_poss = possessions[len(possessions) - 1]
    prev_poss["raw_plays"].append("> {}".format(play))

# Convert raw play data into a nice array of individual plays
def cleanPossessions():
    for poss in possessions:
        new_plays = []
        
        for index in range(0, len(poss["raw_plays"])):
            play = poss["raw_plays"][index]
            
            if play[0] == '>':
                continue
                
            play_arr = play.split(">")
            if play_arr[len(play_arr) - 1].strip() == "Free Throw":
                temp_arr = poss["raw_plays"][index + 1].split(">")
                
                if temp_arr[len(temp_arr) - 1].strip() == "Made":
                    play_arr.append("Made")
                else: play_arr.append("Missed")
                
            for elem in play_arr:
                new_elem = elem.strip()
                
                if new_elem != "Non Possession":
                    new_plays.append(new_elem)
                
        poss["plays"] = copy.copy(new_plays)

# Augment each possession object by computing the points scored and the approximate  
# duration of the possession    
def addStats():
    # Add in points
    possessions[0]["points"] = possessions[0]["score_1"] + possessions[0]["score_2"]
    for index in range(1, len(possessions)):
        points = 0
        prev_poss = possessions[index - 1]
        poss = possessions[index]
        
        if poss["score_1"] != prev_poss["score_1"]:
            points += poss["score_1"] - prev_poss["score_1"]
            
        if poss["score_2"] != prev_poss["score_2"]:
            points += poss["score_2"] - prev_poss["score_2"]
            
        poss["points"] = points
        
    # Add in time duration
    prev_time = '20:00'
    FMT = '%M:%S'
    period = 1
    for index in range(0, len(possessions)):
        poss = possessions[index]
        time = poss["time"]
        if not poss["period"] == period:
            prev_time = '20:00'
            period = poss["period"]
        
        delta = datetime.strptime(prev_time, FMT) - datetime.strptime(time, FMT)
        if datetime.strptime(prev_time, FMT) < datetime.strptime(time, FMT):
            if print_err:
                print("Invalid time: previous ({}) current ({})".format(prev_time, time), file=sys.stderr)
            poss["corrected"] = True
            
            # Approximate duration
            for temp_index in range(index - 2, 0, -1):
                temp_prev_time = possessions[temp_index]["time"]
                if datetime.strptime(temp_prev_time, FMT) > datetime.strptime(time, FMT):
                    delta = datetime.strptime(temp_prev_time, FMT) - datetime.strptime(time, FMT)
                    break
        
        poss["duration"] = delta
        prev_time = time
        
def get_opponents(folder):
    return [f[f.find('-')+1:f.find('.html')] for f in os.listdir(folder) if f.endswith(".html")]

def get_game_files(folder, opponents):
    # In the specified folder, get all of the .html game_files of interest.
    # Each one represents a game of play-by-play data.
    game_files = []
    for file in os.listdir(folder):
        if file.endswith(".html"):
            opponent = file[file.find('-')+1:file.find('.html')]
            if opponent in opponents:
                game_files.append(file)
    return game_files


# MAIN SCRIPT BODY  
if __name__ == "__main__":
    st.title('Synergy Scouting App  :basketball::bar_chart:')
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Team Analysis", "Player Analysis"])
    if page == "Homepage":
        st.markdown('## About the App')
        st.write('We created this app to allow coaches to scout opponent teams with isolated data, which is different from and more useful than the current scouting platform. Coaches can select a team to scout, and then select teams that the scouted team has played to see a comprehensive breakdown of that team’s success in different play types. The coaches can also see breakdown of play types by player, and view helpful data visualizations to guide their decisions.')
        st.markdown('---')
        st.markdown('### Statistics Glossary')
        st.markdown('---')
        st.markdown('### Play Type Glossary')
    else:
        folder = st.sidebar.selectbox('Choose a team to scout', [t.title() for t in TEAMS_TO_SCOUT])
        folder = folder.lower()
        all_opponents = get_opponents(folder)
        opponents = st.sidebar.multiselect('Choose opponents to include in the scouting report', all_opponents)
        if st.sidebar.button('Run!'):
            if opponents == []:
                st.error("Please choose some opponents to include in the analysis.")
                st.stop()
            team = team_mappings[folder] # Team that the analysis will focus on
            module = "sequence_dump"
            game_files = get_game_files(folder, opponents)
            games = []
            teams = {} # List of teams encounters and the possession count of each

            # Loop through each game and create our internal play-by-play structure
            for game in game_files:
                if print_err:
                    print("Game: {}".format(game), file=sys.stderr)
                filename = "{}/{}".format(folder, game)
                with open(filename, 'r') as fp:
                    # Read in the raw html play-by-play site
                    playbyplay = fp.read()
                    
                    # Grab each row ("play") of the play-by-play using a regex
                    regex = r'<tr class="PlayByPlayRow.*?<\/tr>'
                    matches = re.finditer(regex, playbyplay, re.MULTILINE | re.DOTALL)
                    
                    # Initialize parsing variables
                    parser = MyHTMLParser()
                    prev_team = ""
                    prev_period = 1

                    # Extract the data from each play
                    for matchNum, match in enumerate(matches, start=1):
                        tr_text = "{match}".format(match = match.group())
                        parser.feed(tr_text)
                        
                        # Only rows that contain an actual play get parsed
                        if keep_row:
                            if len(raw_data) > 2:
                                # Convert the possession text into structured data
                                possession = makePossession(raw_data)
                                
                                # Add this possession to the appropriate team's possession count
                                if possession["team"] in teams:
                                    teams[possession["team"]] = teams[possession["team"]] + 1
                                else: teams[possession["team"]] = 1
                                
                                # If two adjacent possessions come from the same team in the same period,
                                # merge them
                                if possession["team"] == prev_team and possession["period"] == prev_period:
                                    mergePossession(possession)
                                else: possessions.append(possession)
                                
                                # Update the team and period
                                prev_team = possession["team"]
                                prev_period = possession["period"]
                            else: addPlay(raw_data[1])
                            
                        # Reset for the next row
                        keep_row = False
                        raw_data = []
                        parser.reset()
                
                
                cleanPossessions()
                addStats()
                
                # Add the list of possessions to the games array and reset for the next game
                games.append(copy.deepcopy(possessions))
                possessions = []

            # DONE WITH DATA PARSING AND CLEANING

            # Run whatever analysis you'd like on the data
            stat_module = import_module(module)
            play_type_df, player_stats = stat_module.run_analytics(games, team)

            if page == "Team Analysis":
                st.markdown('### Play Type Breakdown')
                st.dataframe(play_type_df.style.format("{:.2f}"))
                df = stat_module.get_hierarchical_plays(games, team)
                fig = px.treemap(df, path=['A', 'B', 'C'], color_discrete_sequence=px.colors.qualitative.Prism)

                fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
            elif page == "Player Analysis":
                # player_stats_df = player_stats.style.format("{:.2f}")
                roster_img_module = import_module('roster_images')
                st.write(roster_img_module.get_player_headshots(team, player_stats), unsafe_allow_html=True)
        


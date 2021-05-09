import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import plotly.express as px
import streamlit as st

# global variable for all possible play types
SEQUENCES = ["Spot-Up", "Transition", "Post-Up", "P&R Ball Handler", "Cut", "Hand Off", "Offensive Rebound", "Off Screen", "ISO", "P&R Roll Man", "Miscellaneous"]

# tally up keyword-based outcomes of play sequences
# interested in attempts, makes, guarded vs. open, turnovers, and free throws
def tally_stats(play_list):
    tallies = {'attempts': 0, 'makes': 0, 'guarded': 0, 'open': 0, '3PT attempts': 0, '3PT makes': 0, 'turnovers': 0, 'possessions': 0, 'FT attempts': 0, 'FT makes': 0, 'points': 0}
    for single_play in play_list:
        sequence = [event.strip() for event in single_play]
        for event in sequence:
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
                tallies['points'] += 1
                tallies['FT attempts'] += 1
            if event == 'Made':
                tallies['points'] += 1
                tallies['FT makes'] += 1
        tallies['possessions'] += 1
    return tallies

# compute synergy stats from tallied up play / shot outcomes
# stats include: plays / game, points, points per possession, field goals made, 
# field goals attempted, field goal percentage, adjusted field goal percentage,
# turnover rate, and free throw rate
def compute_stats(tallies, game_count):
    # print(tallies)
    stats = {}
    stats['Plays/Game'] = tallies['possessions'] / game_count
    stats['Points'] = tallies['points'] / game_count
    stats['PPP'] = tallies['points'] / tallies['possessions'] if tallies['possessions'] != 0 else np.nan
    stats['FGM'] = tallies['makes'] / game_count
    stats['FGA'] = tallies['attempts'] / game_count
    stats['FG%'] = (stats['FGM'] / stats['FGA']) * 100 if stats['FGA'] != 0 else np.nan
    # https://thesaucereport.wordpress.com/2009/04/28/adjusted-field-goal-percentage/
    stats['aFG%'] = ((stats['Points'] - (tallies['FT makes'] / game_count)) / (2 * stats['FGA'])) * 100 if stats['FGA'] != 0 else np.nan
    stats['TO%'] = (tallies['turnovers'] / tallies['possessions']) * 100 if tallies['possessions'] != 0 else np.nan
    stats['FT%'] = (tallies['FT makes'] / tallies['FT attempts']) * 100 if tallies['FT attempts'] != 0 else np.nan
    return stats

# calculate overall stats based on list of play sequences for each
# given play type or player (the keys of input dictionary)
def get_stats_dict(input_dict, num_games):
    stat_dict = {}
    for key in input_dict.keys():
        tallies = tally_stats(input_dict[key])
        stat_dict[key] = compute_stats(tallies, num_games)
        # print(key, tallies)
    return stat_dict

# parse, split, and clean play-by-play data for filtered subset of games played
# by the team being scouted; returns a dictionary with play types as keys
# and a list of play sequences as values
# e.g. {'Spot-Up': [play 1, play 2, ...], 'Post-Up': [play 1, play 2, ...], ...}
def get_plays_dict(games, team):
    plays_dict = {seq: [] for seq in SEQUENCES}
    for game in games:
        for poss in game:
            if poss["team"] == team:
                sequence = poss["plays"]

                # get a list of all indices at which each keyword play happens
                play_indices = []
                for idx, event in enumerate(sequence):
                    if event in SEQUENCES:
                        # found a play
                        play_indices.append(idx)

                # the possession does not have any play types (e.g. turnover, shot clock violation, etc.)
                if len(play_indices) == 0:
                    continue
                # the possession only has one play type
                elif len(play_indices) == 1:
                    plays_dict[sequence[play_indices[0]]].append(sequence)
                # split up possession with multiple play types into separate sequences
                else:
                    prev_idx = play_indices[0]
                    for play_idx in play_indices[1:]:
                        subplay = sequence[prev_idx-1:play_idx-1]
                        plays_dict[subplay[1]].append(subplay)
                        prev_idx = play_idx
                    subplay = sequence[play_idx-1:]
                    plays_dict[subplay[1]].append(subplay)
    return plays_dict

# go through all play sequences in player-agnostic play type dictionary and 
# sort the plays into a new dictionary with players as keys; the primary player involved in the play should be the first element in the list
# e.g. {'25 Fru Che': [play 1, play 2,...], '3 Devonn Allen': [play 1, ...],...}
def get_player_dict(plays_dict):
    player_dict = {}
    for pt in plays_dict.keys():
        for sequence in plays_dict[pt]:
            player = sequence[0]
            # verify it is a player if token that starts with jersey number
            if player.split(' ')[0].isdigit() and player[2:5] != 'Pts':
                if player not in player_dict.keys():
                    player_dict[player] = []
                player_dict[player].append(sequence)
            else:
                continue
    return player_dict

def get_player_play_dict(player_dict):
    player_play_dict = {player: {seq: [] for seq in SEQUENCES} for player in player_dict}
    for player in player_dict:
        plays = player_dict[player]
        for seq in SEQUENCES:
            # print("--------  " + seq)
            for play in plays:
                if play[1] == seq:
                    # print(play)
                    player_play_dict[player][seq].append(play)
    return player_play_dict

@st.cache(allow_output_mutation=True)
def run_analytics(games, team):
    # Build dictionaries for querying by play type (player agnostic)
    play_type_plays_dict = get_plays_dict(games, team)
    play_type_stat_dict = get_stats_dict(play_type_plays_dict, len(games))
    # Convert to tabular dataframe format for Streamlit display
    play_type_stat_df = pd.DataFrame.from_dict(play_type_stat_dict, orient='index').dropna(subset=['FG%']).round(2)

    # Build dictionaries for querying by player (play type agnostic)
    player_plays_dict = get_player_dict(play_type_plays_dict)
    player_stat_dict = get_stats_dict(player_plays_dict, len(games))
    # Convert to tabular dataframe format for Streamlit display
    player_stat_df = pd.DataFrame.from_dict(player_stat_dict, orient='index').dropna(subset=['FG%']).round(2)

    player_play_dict = get_player_play_dict(player_plays_dict)

    return play_type_plays_dict, play_type_stat_df, play_type_stat_dict, player_stat_df

# get all play sequences and trim them to only focus on first 4 events
# wrangle the data into a dataframe of size (# of plays) x (4)
# make plotly treemap to visualize most frequent plays and subplays
@st.cache(allow_output_mutation=True)
def make_treemap(play_types, play_type_plays_dict, play_type_stats_dict, stat):
    output = []
    for pt in play_types:
        for sequence in play_type_plays_dict[pt]:
            if sequence[1] == pt:
                output.append(sequence[1:5])
    df = pd.DataFrame(output, columns=['A', 'B', 'C', 'D'])
    df[stat] = df['A'].apply(lambda x: round(play_type_stats_dict[x][stat], 2))
    # define a root node to be the parent of the hierarchical data
    df['Overall'] = 'Overall'
    midpoint = np.mean([play_type_stats_dict[key][stat] for key in play_type_stats_dict.keys() if not pd.isna(play_type_stats_dict[key][stat])])
    fig = px.treemap(df, path=['Overall', 'A', 'B', 'C'], color_continuous_scale='RdBu', color_continuous_midpoint=midpoint, color=stat, hover_data={stat:':.2f'})
    # fig.update_traces(marker_cmin=0, marker_cmax=100, marker_cmid = mid, selector=dict(type='treemap'))
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    return fig


# visualize play type efficacy via scatterplot of PPP vs frequency of plays
# each point on the graph represents aggregate stats for each play type 
@st.cache(allow_output_mutation=True)
def make_scatterplot(play_type_df, stat):
    mini_df = play_type_df[['Plays/Game',stat]]
    mini_df['Play'] = play_type_df.index.values
    fig = px.scatter(mini_df,
        x=mini_df["Plays/Game"],
        y=mini_df[stat],
        hover_name=mini_df["Play"],
        hover_data=[stat],
        color="Play"
    )
    fig.update_layout(
        xaxis_title="Plays/Game",
        yaxis_title=stat,
    )
    return fig

# helper function for debugging dictionaries
def print_dict(d):
    for key in d.keys():
        print(key)
        print(d[key])
        print()
# synergy-scouting-app

## About the App

Synergy is a data tracking platform used primarily for scouting purposes in collegiate basketball. Its current bottlenecks include poor organization, poor usability, and lack of practicality in the context of DIII scouting. Most notably, user-facing data tends to be heavily skewed towards landslide games against out-of-conference opponents, rendering insights unactionable. We created this app to enable coaches to scout opponent teams with a filterable subset of games. Coaches can choose a team to scout, select similar caliper opponents that the scouted team has played, and then view a comprehensive breakdown of that team’s strengths and weaknesses through a breakdown play types. The data is displayed in a standard tabular format with complementary data visualizations to drive insights.

## Data Wrangling

Using an HTML parser, this app scrapes collegiate basketball play-by-play data from Synergy. The scraped data looks like the following:

```
{
'team': 'MID', 
'corrected': False, 
'period': '1', 
'time': '18:40', 
'raw_plays': ['5 Max Bosco > P&R Ball Handler > Right P&R > Side > Go Away from Pick > Defense Commits', 'Ball Delivered', '10 Matt Folger > Spot-Up > Drives Right > To Basket > Make 2 Pts', '> Shot > Matt Folger > Any Type > 2 Point Attempt > Make 2 Pts'], 
'score_1': 2, 
'score_2': 2, 
'plays': ['5 Max Bosco', 'P&R Ball Handler', 'Right P&R', 'Side', 'Go Away from Pick', 'Defense Commits', 'Ball Delivered', '10 Matt Folger', 'Spot-Up', 'Drives Right', 'To Basket', 'Make 2 Pts'], 
'points': 2, 
'duration': datetime.timedelta(seconds=17)
}
```

In the above data snippet representing one possession that took place in the first quarter of a game between Amherst and Middlebury, we see many attributes of interest. Since this project focuses on play types, we chose to hone in on the "plays" field. We can observe that in the above play, there was a pick-and-roll (ball handler) play which resulted in a spot-up play thereafter. Given that we wanted to do an analysis of the efficacy of various play types in order to scout an opponent and tailor game preparation based on their strengths and weaknesses, we needed to wrangle this possession data into sequences of events which can be queried by play type and/or player. The following dictionaries form the basis of our project:

### Team-level play type dictionary (sequences of events)

*SCHEME: { 'play type': [play sequence 1, play sequence 2, ...]}*
```
{
'Spot-Up': [['25 Fru Che', 'Spot-Up', 'Drives Right', 'To Basket', 'Turnover'], ['3 Devonn Allen', 'Spot-Up', 'No Dribble Jumper', 'Guarded', 'Long/3pt', 'Make 3 Pts'], ... ], 
'Transition': [['33 Eric Sellew', 'Transition', 'Ballhandler', 'Dribble Jumper', "Short to < 17'", 'Miss 2 Pts'], ... ], 
'Post-Up': [['33 Eric Sellew', 'Post-Up', 'Left Block', 'Left Shoulder', 'Dribble Move', 'To Basket', 'Make 2 Pts'],
'P&R Ball Handler': [['3 Devonn Allen', 'P&R Ball Handler', 'High P&R', 'Dribble Off Pick', 'Defense Commits', 'Turnover'], ... ]
...
}
```

### Team-level play type dictionary (statistics)
*SCHEME: { 'play type': {'stat1': ##.##, 'stat2': ##.##, 'stat3': ##.##, ...}}*
```
{
'Spot-Up': {'Plays/Game': 20.0, 'Points': 23.0, 'PPP': 1.15, 'FGM': 7.0, 'FGA': 17.0, 'FG%': 41.17647058823529, 'aFG%': 64.70588235294117, 'TO%': 10.0, 'FT%': 33.33333333333333}, 
'Transition': {'Plays/Game': 12.0, 'Points': 9.0, 'PPP': 0.75, 'FGM': 3.0, 'FGA': 11.0, 'FG%': 27.27272727272727, 'aFG%': 36.36363636363637, 'TO%': 0.0, 'FT%': 100.0}, 
'Post-Up': {'Plays/Game': 13.0, 'Points': 6.0, 'PPP': 0.46153846153846156, 'FGM': 3.0, 'FGA': 9.0, 'FG%': 33.33333333333333, 'aFG%': 33.33333333333333, 'TO%': 7.6923076923076925, 'FT%': nan}, 
'P&R Ball Handler': {'Plays/Game': 22.0, 'Points': 13.0, 'PPP': 0.5909090909090909, 'FGM': 2.0, 'FGA': 2.0, 'FG%': 100.0, 'aFG%': 250.0, 'TO%': 18.181818181818183, 'FT%': 60.0}
...
}
```


## Usage

Wrangling Testing: `python synergy_parse.py amherst sequence_dump`  
Staging Testing:   `streamlit run app.py`  

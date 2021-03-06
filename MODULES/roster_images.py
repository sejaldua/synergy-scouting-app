import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from Levenshtein import distance as levenshtein_distance

def get_closest_levenshtein(img_dict, player):
    dists = [levenshtein_distance(player, p) for p in img_dict.keys()]
    # print(dists)
    idx = dists.index(min(dists))
    if idx == -1:
        return ""
    return list(img_dict.values())[idx]

def path_to_image_html(img_dict, player):
    try:
        path = img_dict[player]
    except:
        path = get_closest_levenshtein(img_dict, player)
        if path == "":
            return '<img src="''" width="60" >'
    return '<img src="'+ path + '" width="60" >'

def get_headshots(team):
    # Is there a way to have these update each year?
    teams_dict = {'AMH': ('https://athletics.amherst.edu', 
                            '/sports/mens-basketball/roster?path=mbball'),
                'BAT': ('https://gobatesbobcats.com', 
                            '/sports/mens-basketball/roster/2019-20'), 
                'COL': ('https://colbyathletics.com', 
                            '/sports/mens-basketball/roster/2019-20'), 
                'HC': ('https://athletics.hamilton.edu', 
                            '/sports/mens-basketball/roster/2019-20'), 
                'TCT': ('https://bantamsports.com', 
                            '/sports/mens-basketball/roster/2019-20'), 
                'MID': ('https://athletics.middlebury.edu', 
                            '/sports/mbball/roster/2019-20')}

    # print("GETTING HEADSHOTS", team)
    site = teams_dict[team][0]
    ext = teams_dict[team][1]
    url = site + ext

    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all(class_ = 'lazyload')

    # dict: {alt: data-src}  
    urls = [site + img['data-src'] for img in img_tags]
    names = [img['alt'] for img in img_tags]
    img_dict = {names[i].lower():urls[i] for i in range(len(names))}
    return img_dict

def get_player_headshots(team, df):
    df.sort_values(by='Points', ascending=False, inplace=True)
    img_dict = get_headshots(team)
    # print(img_dict.keys())
    images = [path_to_image_html(img_dict, " ".join(x.split()[1:]).lower()) for x in list(df.index)]
    try:
        df.insert(0, 'Headshot', images)
    except:
        pass
    return df.to_html(escape=False)
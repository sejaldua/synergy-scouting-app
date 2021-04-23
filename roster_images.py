import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

def path_to_image_html(path):
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

    print("GETTING HEADSHOTS", team)
    site = teams_dict[team][0]
    ext = teams_dict[team][1]
    url = site + ext

    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all(class_ = 'lazyload')

    # dict: {alt: data-src}  
    urls = [site + img['data-src'] for img in img_tags]
    names = [img['alt'] for img in img_tags]
    img_dict = {names[i]:urls[i] for i in range(len(names))}

    player_df = pd.DataFrame.from_dict(img_dict, orient='index', columns=['headshot'])
    player_df['headshot'] = player_df['headshot'].apply(lambda x: path_to_image_html(x))

    # Rendering the dataframe as HTML table
    return player_df.to_html(escape=False)
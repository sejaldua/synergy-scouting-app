import re
import requests
from bs4 import BeautifulSoup

# Is there a way to have these update each year?
teams_dict = {'Amherst': ('https://athletics.amherst.edu', 
                        '/sports/mens-basketball/roster?path=mbball'),
             'Bates': ('https://gobatesbobcats.com', 
                        '/sports/mens-basketball/roster/2019-20'), 
             'Colby': ('https://colbyathletics.com', 
                        '/sports/mens-basketball/roster/2019-20'), 
             'Hamilton': ('https://athletics.hamilton.edu', 
                        '/sports/mens-basketball/roster/2019-20'), 
             'Trinity': ('https://bantamsports.com', 
                        '/sports/mens-basketball/roster/2019-20'), 
             'Middlebury': ('https://athletics.middlebury.edu', 
                        '/sports/mbball/roster/2019-20')}

team_rosters_dict = {}

for team in teams_dict:
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
    team_rosters_dict[team] = img_dict

print(team_rosters_dict)
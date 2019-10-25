import requests
from bs4 import BeautifulSoup

class Team:
    def __init__(self, name):
        self.name = name
        self.beatenTeams = []

    def addOpponent(self, opp):
        self.beatenTeams.append(opp)

# list of teams
result = requests.get("https://www.sports-reference.com/cfb/schools/")
src = result.content
soup = BeautifulSoup(src, 'lxml')
schools = []

# grab the first row of the table
team = soup.tbody.tr

while team != None:
    #skip the headers throughout the table
    if team.has_attr('class'):
        team = team.find_next_sibling()
        team = team.find_next_sibling()
    
    # print(team.td.find_next_sibling().find_next_sibling().get_text())

    # only grab the schools that have played this year
    if team.td.find_next_sibling().find_next_sibling().get_text() == "2019":
        schools.append(team.a.get_text())

    # go to next team, if on last team, will be equal None
    team = team.find_next_sibling()
   
teams = {}

# create a Team object for each school
for school in schools:
    teams[school] = Team(school)

# to catch teams that were referenced by different names than in the list of teams
teams["Mississippi"] = teams["Ole Miss"]
teams["Pittsburgh"] = teams["Pitt"]
teams["Texas-San Antonio"] = teams["UTSA"]
teams["Texas-El Paso"] = teams["UTEP"]
teams["Southern California"] = teams["USC"]
teams["UNLV"] = teams["Nevada-Las Vegas"]
teams["Central Florida"] = teams["UCF"]
teams["Alabama-Birmingham"] = teams["UAB"]

# index of all games played this year
gamesPlayedURL = "https://www.sports-reference.com/cfb/play-index/sgl_finder.cgi?request=1&match=game&year_min=2019&year_max=2019&order_by=date_game&order_by_asc=Y"
result = requests.get(gamesPlayedURL)
src = result.content
soup = BeautifulSoup(src, 'lxml')
game = soup.tbody.tr

def getNextButton(tag):
    return tag.name == 'a' and tag.get_text() == "Next Page" and tag.has_attr('href')

# counter used to count number of games read on the page, if less than 100 then the end of the list has been reached
counter = 0
while True:
    while game != None:
        # skip the headers throughout the table
        if game.has_attr('class'):
            game = game.find_next_sibling()
        counter += 1
        # grab only the games where the first team won (prevents duplicates)
        if game.td.find_next_sibling().find_next_sibling().find_next_sibling().find_next_sibling().find_next_sibling().get_text() == "W":
            winningTeam = game.a.get_text()
            
            # ignore cases where the second team does not have an a tag (aka not a d1 fbs school)
            if len(game.td.find_next_sibling().find_next_sibling().find_next_sibling().find_next_sibling().find_all("a")) > 0:
                losingTeam = game.td.find_next_sibling().find_next_sibling().find_next_sibling().find_next_sibling().a.get_text()
                teams.get(winningTeam).addOpponent(teams[losingTeam])
        
        
        game = game.find_next_sibling()
    
    # if not getNextButton(soup):
    #     break
    
    # for tag in soup.findAll(getNextButton):
    #     nextButton = tag['href']

    if counter % 100 == 0:
        nextPage = gamesPlayedURL + "&offset=" + str(counter)
        result = requests.get(nextPage)
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        game = soup.tbody.tr
    
    else:
        break

#print("done")

visitedComplete = {}
visitedNotComplete = {}

for team in teams:
    visitedComplete[team] = False
    visitedNotComplete[team] = False

for team in teams:
    it = team




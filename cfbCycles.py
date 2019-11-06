import requests
from bs4 import BeautifulSoup

class Team:
    def __init__(self, name, val):
        self.name = name
        self.beatenTeams = []
        self.inCurCycle = False
        self.val = val # used in the algorithm to find cycles, will just be the teams placement in alphabetical order

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
counter = 0
for school in schools:
    counter += 1
    teams[school] = Team(school, counter) 

numSchools = counter

# to catch teams that were referenced by different names than in the list of teams
teams["Mississippi"] = teams["Ole Miss"]
teams["Pittsburgh"] = teams["Pitt"]
teams["Texas-San Antonio"] = teams["UTSA"]
teams["Texas-El Paso"] = teams["UTEP"]
teams["Southern California"] = teams["USC"]
teams["UNLV"] = teams["Nevada-Las Vegas"]
teams["Central Florida"] = teams["UCF"]
teams["Alabama-Birmingham"] = teams["UAB"]
teams["Southern Methodist"] = teams["SMU"]

# index of all games played this year
gamesPlayedURL = "https://www.sports-reference.com/cfb/play-index/sgl_finder.cgi?request=1&match=game&year_min=2019&year_max=2019&order_by=date_game&order_by_asc=Y"
result = requests.get(gamesPlayedURL)
src = result.content
soup = BeautifulSoup(src, 'lxml')
game = soup.tbody.tr

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

# I will be implementing the algorithm found here:
# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.516.9454&rep=rep1&type=pdf
# which will find all elementary cycles in the graph formed from the teams.
# From there it will be a matter of finding the longest cycle.

# the algorithm calls for an n * n array where n is the number of nodes to keep track of closures
# For this implementation, we will create a list of n+1 variable lists, n+1 to keep the indexing
# consistent with the team vals, and allow the size of the list to keep track of "left most 0"
closures = [[] for i in range(numSchools + 1)]

currentCycle = []
listOfCycles = []

# pass in the teamVals
def isTeamClosed(teamToCheck, closedTo):
    i = 0
    for closedTeamVal in closures[closedTo]:
        if teamToCheck == closedTeamVal:
            return True
        i += 1
    return False

for team in teams:
    curTeam = teams[team]
    curTeam.inCurCycle = True
    currentCycle.append(curTeam)
    while True:
        noTeamFoundFlag = True
        #EC2
        for beatenTeam in curTeam.beatenTeams:
            if beatenTeam.val > curTeam.val and not beatenTeam.inCurCycle and not isTeamClosed(beatenTeam.val, curTeam.val):
                beatenTeam.inCurCycle = True
                currentCycle.append(beatenTeam)
                curTeam = beatenTeam
                noTeamFoundFlag = False
                break
        
        if noTeamFoundFlag:
            #EC3
            for beatenTeam in curTeam.beatenTeams:
                if beatenTeam.val == teams[team].val:
                    listOfCycles.append(list(currentCycle))

            #EC4
            if len(currentCycle) == 1:
                break

            closures[curTeam.val].clear()
            currentCycle.pop().inCurCycle = False
            closures[currentCycle[-1].val].append(curTeam.val)
            curTeam = currentCycle[-1]

    currentCycle.clear()
    for closureList in closures:
        closureList.clear()

maxCycle = []
for cycle in listOfCycles:
    if len(cycle) > len(maxCycle):
        maxCycle = cycle

for team in maxCycle:
    print(team.name)
            




        
        







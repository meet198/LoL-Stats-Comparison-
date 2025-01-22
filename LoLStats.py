import requests
import matplotlib.pyplot as plt
import numpy as np

api_url = 'http://ddragon.leagueoflegends.com/cdn/13.1.1/data/en_US/champion.json'
response = requests.get(api_url) #Requests League of Legends API URL 

#Checks if response from API is valid
if response.status_code == 200:
    data = response.json()
else:
    print ("Error: " + str(response.status_code))
    exit()

#Creates empty array with 162 elements (because there are 162 champions in the game)
stat = np.empty(162, dtype=int) #Tracks the specific inputted stat of each champion
role = np.empty(162, dtype="<U10") #Tracks role of each champion

#Creates empty dic with keys 1-18 (for each level. Max level is 18 for a champion in League of Legends)
statPerLevel = dict.fromkeys(range(1,19)) #Stat of the specific inputted champion per level 
avgStatPerLevel = dict.fromkeys(range(1,19)) #Average stat for all champions in the inputted champions role

avgStatPerRole = np.zeros(6, dtype=float) #Average inputted stat for each role type (array of 6 for 6 types of roles)

'''
Below dictionary is used to calculate average stat per role and average stat per level
Keys are the different role types
Index 0 is sum of all the stat values per role
Index 1 is the sum of all stat increase per level values per role
Index 2 is a counter for each role
Index 3 is index 1/ index 2 (average stat increase per level value per role)
'''
statPerRole = {
    'Fighter': [0,0,0,0],
    'Mage': [0,0,0,0], 
    'Assassin': [0,0,0,0], 
    'Marksman': [0,0,0,0], 
    'Tank': [0,0,0,0], 
    'Support': [0,0,0,0]
}

#Function used to see the distribution of a stat per role and can show how a specific champions stat compares to the average
def getAvg (input, champion): 
    i = 0

    #Name below is used to iterate through all champions 
    for name in data['data']:
        stat[i] = data['data'][name]['stats'][input]
        role[i] = data['data'][name]['tags'][0]
        
        #Not all champions use Mana, so below statement is used to remove them from the average calculation as to not skew it
        if data['data'][name]['partype'] != 'Mana' and input == 'mp': 
            stat[i] = 0
            role[i] = ''
            i += 1
            continue
        
        statPerRole[role[i]][0] += stat[i]

        #If statement for movespeed stat as there is no movespeedperlevel stat
        if input != 'movespeed': statPerRole[role[i]][1] += data['data'][name]['stats'][input + 'perlevel']
        statPerRole[role[i]][2] += 1
        
        i += 1
    
    #Used to calculate average stat per role and stat incrase per level per role
    for j, k in zip(statPerRole, range(6)): 
        avgStatPerRole[k] = statPerRole[j][0] / statPerRole[j][2]
        statPerRole[j][3] = statPerRole[j][1] / statPerRole[j][2]

    #Used to get data for the specific inputted champion and the averages for stats in that specific role
    if champion != '':
        championRole = data['data'][champion]['tags'][0] #Gets the role of the inputted champion
        statPerLevel[1] = data['data'][champion]['stats'][input] #Gets the base stat for inputted champion

        #Gets average base stat for role of the inputted champion
        avgStatPerLevel[1] = statPerRole[championRole][0] / statPerRole[championRole][2]

        #Gets value for each level 
        for i in range(2,19):
            if input != 'movespeed':
                statPerLevel[i] = statPerLevel[i-1] + data['data'][champion]['stats'][input + 'perlevel'] #This is for inputted champion
            avgStatPerLevel[i] = avgStatPerLevel[i-1] + statPerRole[championRole][3] #This is for the average of the role 

    plot(champion, input)

#Plots all the data calculated above
def plot(champion, inputStat):
    fig, (ax1, ax2) = plt.subplots(1,2, figsize=(15,8))
    ax1.scatter(role[role != ''],stat[stat != 0], label='Each champion') #Plot of inputted stats per champion separated by roles
    ax1.scatter(statPerRole.keys(), avgStatPerRole, label='Average per role') #Plot of average inputted stat separated by role
    ax1.set_xlabel('Role')
    ax1.set_ylabel('Base ' + inputStat.title())
    ax1.set_title('Base ' + inputStat.title() + ' Per Role')
    ax1.legend()

    if champion != '':
        #Plots the stat of the specific inputted champion to compare with rest of the champions and the average
        ax1.scatter(data['data'][champion]['tags'][0], data['data'][champion]['stats'][inputStat], label=champion)
        ax1.legend(loc='best')

        #Second plot to see how the stata increases for the champion compared to the average increase
        ax2.plot(avgStatPerLevel.keys(), avgStatPerLevel.values(), '-', label='Average per role')
        ax2.plot(statPerLevel.keys(), statPerLevel.values(), '.', label=champion)
        ax2.set_xlabel('Level')
        ax2.set_ylabel(inputStat.title())
        ax2.set_xticks(range(1, 19, 1))
        ax2.set_title(inputStat.title() +' Increase Per Level')
        ax2.legend()

    plt.show()

'''
Stats that can be compared: 
[hp, mp, movespeed, armor, spellblock, attackrange, hpregen, mpregen, crit, attackdamage, attackspeed]
mp = mana, spellblock = magic resist
'''

inputStat = 'armor'
champion = 'Shen'
getAvg (inputStat,champion)

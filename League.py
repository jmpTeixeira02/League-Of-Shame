#encoding: utf-8

from riotwatcher import LolWatcher, ApiError
import csv
import asyncio
import random

import DB

EUROPE = "euw1"

# ------------------- FILE HANDLING ------------------------

import os

League_Api_Key= os.environ["League_Api_Key"]

DB.create_table()

csvSums = []
csvIDs = []
csvServer = []

fraseFelix = [[],[],[],[],[]]
fraseSopas = [[],[],[],[],[]]

SOPAS = 152057225316270081
FELIX = 249609103737880576

# Get the summoners from the csv
with open("CSV/summoner.csv") as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        csvSums.append(row[0])
        csvIDs.append(row[1])
        csvServer.append(row[2])

def func(list, row):
    i = int(row[1])
    if (i <= 5):
        list[i-1].append(row[2])
#
# Get the phrases from csv
with open("CSV/frase.csv", encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        if row[0] == "FELIX":
            func(fraseFelix, row)
        elif row[0] == "SOPAS":
            func(fraseSopas, row)
        elif row[0] == "GERAL":
            func(fraseFelix, row)
            func(fraseSopas, row)

# Dar load dos users para a DB
def loading():
    for x in range(1,len(csvSums)):
        DB.Insert_Into_Database(csvSums[x],0,csvIDs[x],csvServer[x])

#loading()

Summoners = DB.Summoner_Info()

LOL_API = LolWatcher(League_Api_Key)

# ---------------------------------------------------------


# Get and print the summoner ranked stats
def user_ranked_stats(Region, User):
    stats = LOL_API.league.by_summoner(Region, User["id"])
    if len(stats) > 1:
        #print(User["name"] + ": " + stats[1]["tier"], stats[1]["rank"])
        return (stats[1]["tier"],stats[1]["rank"])
    if len(stats) == 0:
        stats = [{"tier": "UNRANKED", "rank": ""}]
    #print(User["name"] + ": " + stats[0]["tier"], stats[0]["rank"])
    return (stats[0]["tier"],stats[0]["rank"])

# Get the summoner last match
def user_last_match(Region, User):
    matches = LOL_API.match.matchlist_by_account(Region, User["accountId"])
    lastmatch = matches["matches"][0]
    lastmatch_data = LOL_API.match.by_id(Region, lastmatch["gameId"])
    return lastmatch_data

# Find the participantId of the user in the match
def find_participantId(Summoner_Match, User):
    for x in range(len(Summoner_Match)):
        if Summoner_Match[x]["player"]["accountId"] == User["accountId"]:
            return Summoner_Match[x]["participantId"]

RankCalculator = {"I": 4, "II":3, "III":2, "IV":1, "":0,"IRON":10,"BRONZE":20, "SILVER":30,"GOLD":40,"PLATINUM":50,"DIAMOND":60,"MASTER":70,"GRANDMASTER":80,"CHALLENGER":90,"UNRANKED":0, None:0}

def Calculate_Rank(rank_new,tier_new,rank_old,tier_old):
    print("RANK_NEW: ",rank_new," TIER_NEW ", tier_new, " RANK_OLD: ", rank_old, " TIER_OLD: ", tier_old)
    if ((RankCalculator[rank_new] + RankCalculator[tier_new]) - (RankCalculator[rank_old] + RankCalculator[tier_old]) == 0):
        return 0
    elif ((RankCalculator[rank_new] + RankCalculator[tier_new]) - (RankCalculator[rank_old] + RankCalculator[tier_old]) > 0):
        #SUBIU
        return 5
    else:
        #DESCEU
        return 4

# Iterate through all summoners
def Get_Statistics(Summoner_Data):

    User = DB.get_user(Summoner_Data[0])

    lastmatch = user_last_match(EUROPE, User)

    # Get the ID of the last match
    lastmatch_id = lastmatch["gameId"]

    #Verifies if there is a new game and add it to the Database
    if (Summoner_Data[1] == lastmatch_id):
        #print("There are no new matches!")
        return False
    else:
        DB.Update_database_lastmatch(Summoner_Data[0], lastmatch_id)

    # Get the info about each summoner in the last match
    Summoner_Match = lastmatch["participantIdentities"]

    # Find the participantId of the user in the match
    ID_Participant = find_participantId(Summoner_Match, User)

    # Print the info about the summoner in the match
    Summoner_Details = (lastmatch["participants"][ID_Participant - 1])

    # Summoner_Statistics = ["Kills", "Deaths", "Assists", "CS", "Win", "GameTime (s)", "GameMode"]
    return [Summoner_Details["stats"]["kills"], Summoner_Details["stats"]["deaths"], Summoner_Details["stats"]["assists"], Summoner_Details["timeline"]["lane"], Summoner_Details["timeline"]["role"],Summoner_Details["stats"]["totalMinionsKilled"], Summoner_Details["stats"]["win"], lastmatch["gameDuration"], lastmatch["gameMode"]]


def Get_True_Role(Lane, Role):
    if ((Lane == "BOT" or Lane == "BOTTOM") and (Role == "DUO_CARRY")):
        return "AD"
    elif ((Lane == "BOT" or Lane == "BOTTOM") and (Role == "DUO_SUPPORT")):
        return "SUPPORT"
    elif (Lane == "TOP"):
        return "TOP"
    elif (Lane == "MID" or Lane == "MIDDLE"):
        return "MID"
    elif (Lane == "JUNGLE"):
        return "JUNGLE"
    

def Calculate_Shame(Details):
    Kills = Details[0]
    Deaths = Details[1]
    Assists = Details[2]
    Lane = Details[3]
    Role = Details[4]
    True_Role = Get_True_Role(Lane, Role)
    Minions = Details[5]
    Win_Status = Details[6]
    Duration = Details[7]
    Gamemode = Details[8]

    if (Gamemode == "CLASSIC" or Gamemode == "ONEFORALL"):
        if Deaths == 0:
            Deaths = 1

        # If lose before 22min
        if (not Win_Status and Duration <= 1320):
            return 1
        elif ((Kills + Assists * 0.5) / Deaths < 0.85):
            return 2
        # MINION / MIN < 6.5
        elif (True_Role != "SUPPORT" and True_Role != "JUNGLE" and (Minions / (Duration / 60) < 6.3)):
            return 3
        else:
            return 0
    return 0

def getrandom(Type, list):
    rndm = random.randint(0,len(list[Type-1]) - 1)
    return list[Type-1][rndm]

def Burn(Type, Server):
    if Server == SOPAS:
        return getrandom(Type, fraseSopas)
    elif Server == FELIX:
        return getrandom(Type, fraseFelix)
    else:
        return "NOT"


def Final(Summoner):
    Summoner_Statistics = Get_Statistics(Summoner)
    if (not Summoner_Statistics):
        return "NOT"
    print(Summoner_Statistics)
    
    Type = Calculate_Shame(Summoner_Statistics)
    if Type == 0 or Type == None:
        return "NOT"
    return (Burn(Type, Summoner[3]))

def Get_rank(Summoner):
    Summoner_Name = Summoner[0]
    User = DB.get_user(Summoner_Name)

    # Print the user ranked stats
    User_Info = user_ranked_stats(EUROPE, User)
    fetched = DB.Update_database_rank(Summoner_Name,User_Info[0],User_Info[1])
    if (fetched == False):
        return "NOT"
        
    Type = Calculate_Rank(User_Info[0], User_Info[1], fetched[0],fetched[1])
    if Type == 0:
        return "NOT"
    return (Burn(Type, Summoner[3]))
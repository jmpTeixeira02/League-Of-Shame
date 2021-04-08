import os

League_Api_Key= os.environ["League_Api_Key"]

from riotwatcher import LolWatcher, ApiError

EUROPE = "euw1"

LOL_API = LolWatcher(League_Api_Key)

def load_user_for_db(Summoner_Name):
    # Get the user ID
    try:
        User = LOL_API.summoner.by_name(EUROPE, Summoner_Name)
    except ApiError as error:
        if error.response.status_code == 429:
            print("Too many requests")
        elif error.response.status_code == 404:
            print("Username Error")
        else:
            raise
    return User
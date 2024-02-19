from datetime import datetime
from account_statsV4 import *
import time
summonerNames = ["ironsuperhulk", "DooJ", " impreg the keg", "Jeeveezee", "BluezamX", "yvan i am"]
now = datetime.now()
done = False
current_hour = now.strftime("%H")

if current_hour == "11" and done == False:
    for summoner in summonerNames:
        print("Summoner: ",summoner)
        getStats(summoner)
    done = True

if current_hour == "21":
    done = False

time.sleep(60*60)

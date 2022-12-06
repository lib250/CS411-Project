from django.shortcuts import render, redirect
from django.http import  HttpResponse, HttpResponseRedirect
import requests 
from django.template import loader
from riotwatcher import LolWatcher, ApiError
import pandas as pd
import json

# Create your views here.
from .forms import NameForm
import urllib.parse
def index(request):
    template = loader.get_template('input.html')

    return  HttpResponse(template.render())
#RGAPI-41cbb789-b621-4522-acef-e5211ecfc836
#Regions, inputted lower case
#EUN1, EUW1	JP1	KR	LA1	LA2 NA1	OC1	TR1	RU BR1


def get_summoner(request):
    #checks valididy of form
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            params = {
                "your_name" : form.cleaned_data['name'],
                "your_region" : form.cleaned_data['region']
            }
        q_string = urllib.parse.urlencode(params)
        
       
        nameregiondict = q_string
        #gets name from qstring
        name = nameregiondict.split("&")
        name = name[0].split("=")
        name = name[1] 
        #gets region from qstring
        my_region = nameregiondict.split("&")
        my_region = my_region[1].split("=")
        my_region = my_region[1]
        #riot api form, gets data
        #match list
        api_key = 'RGAPI-cb37496a-27b4-40a3-b34b-faad97db50f4'
        watcher = LolWatcher(api_key)
        me_info = watcher.summoner.by_name(my_region, name)
        #gets account id
        me = me_info['id']
        puuid = me_info['puuid']
        ranked_stats = watcher.league.by_summoner(my_region, me)
        #leagueID = ranked_stats[0]['id']
        name = ranked_stats[0]['summonerName']
        rank, tier = ranked_stats[0]['rank'], ranked_stats[0]['tier'] 
        rankTier =  tier +rank 
        #gets matches using puuid
        my_matches = watcher.match.matchlist_by_puuid(my_region, puuid, 0, 10)
        last_match = my_matches[0]

        match_detail = watcher.match.by_id(my_region, last_match)
        
        
        #participants = []
        #for row in match_detail['participants']:
            #participants_row = {}
            #participants_row['champion'] = row['championId']
            #participants_row['spell1'] = row['spell1Id']
            #participants_row['spell2'] = row['spell2Id']
            #participants_row['win'] = row['stats']['win']
            #participants_row['kills'] = row['stats']['kills']
            #participants_row['deaths'] = row['stats']['deaths']
            #participants_row['assists'] = row['stats']['assists']
            #participants_row['totalDamageDealt'] = row['stats']['totalDamageDealt']
            #participants_row['goldEarned'] = row['stats']['goldEarned']
            #participants_row['champLevel'] = row['stats']['champLevel']
            #participants_row['totalMinionsKilled'] = row['stats']['totalMinionsKilled']
            #participants_row['item0'] = row['stats']['item0']
            #participants_row['item1'] = row['stats']['item1']
            #participants.append(participants_row)
        #df = pd.DataFrame(participants)
        
        


        
        #name = name[summonerName]

 
        return render(request, 'display.html', {'response': ranked_stats, 'name': name, 'rank':rankTier, 'matches' : match_detail})
        #if form.is_valid():
           # name = form.cleaned_data['your_name']
            #region = form.cleaned_data['your_region'] 
    else:
        form = NameForm()
        return render(request, "data.html", {"form":form})


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
api_key = 'RGAPI-4d81e2ca-333c-412a-af76-c3fae7638134'
        
watcher = LolWatcher(api_key)
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
        last_10_games = match_creator(my_matches, my_region)
        match_detail = watcher.match.by_id(my_region, last_match)
        info = match_detail['info']
        participants_info = info['participants']
        #gets info from 1 game and puts it in a array of dictionaries
        participants = []
        for row in participants_info:
            participants_row = {}
            participants_row['summoner'] = row['summonerName']
            participants_row['champion'] = row['championName']
            participants_row['spell1'] = row['spell1Casts']
            participants_row['spell2'] = row['spell2Casts']
            participants_row['win'] = row['win']
            participants_row['kills'] = row['kills']
            participants_row['deaths'] = row['deaths']
            participants_row['assists'] = row['assists']
            participants_row['totalDamageDealt'] = row['totalDamageDealt']
            participants_row['goldEarned'] = row['goldEarned']
            participants_row['champLevel'] = row['champLevel']
            participants_row['totalMinionsKilled'] = row['totalMinionsKilled']
            participants_row['item0'] = row['item0']
            participants_row['item1'] = row['item1']
            participants.append(participants_row)
        
        
        


        
        #name = name[summonerName]

 
        return render(request, 'display.html', {'response': ranked_stats, 'name': name, 'rank': rankTier, 'participants' : participants, 'matches' : last_10_games})
        #if form.is_valid():
           # name = form.cleaned_data['your_name']
            #region = form.cleaned_data['your_region'] 
    else:
        form = NameForm()
        return render(request, "data.html", {"form":form})
#creates a list of the 10 matches played, which each match contains a dictinary of ach player
def match_creator(list_matches, region):
    ten_match_detail = []
    for i in list_matches:
        match_detail = watcher.match.by_id(region,i)
        info = match_detail['info']
        participants_info = info['participants']     
        participants = []
        for row in participants_info:
            participants_row = {}
            participants_row['summoner'] = row['summonerName']
            participants_row['champion'] = row['championName']
            participants_row['spell1'] = row['spell1Casts']
            participants_row['spell2'] = row['spell2Casts']
            participants_row['win'] = row['win']
            participants_row['kills'] = row['kills']
            participants_row['deaths'] = row['deaths']
            participants_row['assists'] = row['assists']
            participants_row['totalDamageDealt'] = row['totalDamageDealt']
            participants_row['goldEarned'] = row['goldEarned']
            participants_row['champLevel'] = row['champLevel']
            participants_row['totalMinionsKilled'] = row['totalMinionsKilled']
            participants_row['item0'] = row['item0']
            participants_row['item1'] = row['item1']
            participants.append(participants_row)
        ten_match_detail.append(participants)
    return ten_match_detail
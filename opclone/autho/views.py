from django.shortcuts import render, redirect
from django.http import  HttpResponse, HttpResponseRedirect
import requests 
from django.template import loader
from django.contrib import messages
from riotwatcher import LolWatcher, ApiError
import pandas as pd
import json

from .models import SearchHistory

# Create your views here.
import urllib.parse
def index(request):
    template = loader.get_template('input.html')

    return  HttpResponse(template.render())
#RGAPI-41cbb789-b621-4522-acef-e5211ecfc836
#Regions, inputted lower case
#EUN1, EUW1	JP1	KR	LA1	LA2 NA1	OC1	TR1	RU BR1
api_key = 'RGAPI-4d81e2ca-333c-412a-af76-c3fae7638134'
valid_regions = {'eun1', 'euw1', 'jp1', 'kr', 'la1', 'la2', 'na1', 'oc1', 'tr1', 'ru', 'br1'}
        
watcher = LolWatcher(api_key)
def get_summoner(request):
    
    ### Get user search history if logged in
    user_search_history = []
    if request.user.is_authenticated:
        entry_exists = SearchHistory.objects.filter(uid=request.user.username)
        if entry_exists:
            user_search_history = SearchHistory.objects.get(uid=request.user.username).history.split(';')
    
    if request.method == 'POST':
        
        ### Get input info from user
        if 'preset' in request.POST:
            print(len(request.POST['preset']))
            name, my_region = request.POST['preset'].split(',')
        else:
            name = request.POST['summoner_name']
            my_region = request.POST['region']
        
        ### Error checking
        if my_region not in valid_regions:
            messages.info(request, 'Please enter a valid region.')
            return redirect('test')
        
        try:
            me_info = watcher.summoner.by_name(my_region, name)
        except ApiError:
            messages.info(request, 'Summoner not found.')
            return redirect('test')
        
        ### Updates database to reflect user's new search history
        if request.user.is_authenticated:
            entry_exists = SearchHistory.objects.filter(uid=request.user.username)
            if not entry_exists:
                new_history = SearchHistory.objects.create(uid=request.user.username, history=name+','+my_region)
                new_history.save()
            else:
                history_entry = SearchHistory.objects.get(uid=request.user.username)
                history = history_entry.history.split(';')
                current_entry = name + ',' + my_region
                
                current_entry_idx = -1
                for i in range(len(history)):
                    if history[i] == current_entry:
                        current_entry_idx = i
                        
                if current_entry_idx > -1:
                    temp = history[current_entry_idx]
                    while current_entry_idx > 0:
                        history[current_entry_idx] = history[current_entry_idx - 1]
                        current_entry_idx -= 1
                    history[0] = temp
                else:
                    history = [current_entry] + history
                    
                if len(history) >= 6:
                    history.pop()
                
                history_entry.history = ';'.join(history)
                history_entry.save()
        
        #gets account id
        me = me_info['id']
        puuid = me_info['puuid']
        ranked_stats = watcher.league.by_summoner(my_region, me)
        name = me_info['name']
        rank, tier = (ranked_stats[0]['rank'], ranked_stats[0]['tier']) if ranked_stats else ("None", "None")
        rankTier =  tier + " " +rank 
        #gets matches using puuid
        my_matches = watcher.match.matchlist_by_puuid(my_region, puuid, 0, 10)
        
        last_10_games = match_creator(my_matches, my_region)
       
        return render(request, 'data.html', {'response': ranked_stats, 'name': name, 'rank': rankTier, 'matches': last_10_games, 'history': user_search_history})
        
    else:
        return render(request, 'data.html', {'history': user_search_history})
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
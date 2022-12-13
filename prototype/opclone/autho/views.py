from django.shortcuts import render, redirect
from django.http import  HttpResponse, HttpResponseRedirect
import requests 
from django.template import loader
from django.contrib import messages
from riotwatcher import LolWatcher, ApiError
import spotipy
import spotipy.oauth2
from spotipy.oauth2 import SpotifyClientCredentials




import json

from .models import SearchHistory

# Create your views here.

#RGAPI-41cbb789-b621-4522-acef-e5211ecfc836
#Regions, inputted lower case
#EUN1, EUW1	JP1	KR	LA1	LA2 NA1	OC1	TR1	RU BR1
api_key = 'RGAPI-f0d7899d-b773-4378-a238-bbbe5ecf5375'
valid_regions = {'eun1', 'euw1', 'jp1', 'kr', 'la1', 'la2', 'na1', 'oc1', 'tr1', 'ru', 'br1'}
        
watcher = LolWatcher(api_key)
def get_summoner(request):
    
    ### Get user search history if logged in
    user_search_history = []
    if request.user.is_authenticated:
        entry_exists = SearchHistory.objects.filter(uid=request.user.username)
        if entry_exists:
            user_search_history = SearchHistory.objects.get(uid=request.user.username).history
            user_search_history = [' from '.join(entry.split(',')) for entry in user_search_history.split(';')]
    
    ### If the user has searched for a summoner
    if request.method == 'POST':
        
        ### Get input info from user
        if 'preset' in request.POST:
            # If button was pressed
            name, my_region = request.POST['preset'].split(' from ')
        else:
            # Search field was used
            name = request.POST['summoner_name']
            my_region = request.POST['region']
        
        ### Error checking
        if my_region not in valid_regions:
            messages.info(request, 'Please enter a valid region. Valid regions include eun1, euw1, jp1, kr, la1, la2, na1, oc1, tr1, ru, and br1.')
            return redirect('test')
        
        try:
            me_info = watcher.summoner.by_name(my_region, name)
        except ApiError:
            messages.info(request, 'Summoner not found.')
            return redirect('test')
            
        # Gets player information
        me = me_info['id']
        puuid = me_info['puuid']
        ranked_stats = watcher.league.by_summoner(my_region, me)
        name = me_info['name']
        rank, tier = (ranked_stats[0]['rank'], ranked_stats[0]['tier']) if ranked_stats else ("None", "None")
        rankTier =  tier + " " +rank 
        
        # Gets matches using puuid
        my_matches = watcher.match.matchlist_by_puuid(my_region, puuid, 0, 10)
       

        last_10_games, streak_win, streak_len = match_creator(name, my_matches, my_region)
        
        ### Updates database to reflect user's new search history
        if request.user.is_authenticated:
            update_database(request.user.username, name, my_region)
       
        return render(request, 'data.html', {'history': user_search_history, 'response': ranked_stats, 
                                             'name': name, 'rank': rankTier, 'matches': last_10_games,
                                             's_win': streak_win, 's_len': streak_len})
        
    else:
        return render(request, 'data.html', {'history': user_search_history})
    
### Creates a list of the 10 matches played; each match contains a dictionary of each player
def match_creator(curr_summoner, list_matches, region):
    ten_match_detail = {}
    
    latest_game = True
    streak_going = True
    streak_win = False
    streak_len = 0
    
    for i in list_matches:
        match_detail = watcher.match.by_id(region,i)
        info = match_detail['info']
        participants_info = info['participants']     
        game_info = []
        gameType = info['gameMode']
        gameTime = info['gameDuration'] // 60
        game_info = [gameType, gameTime]
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
            
            # Find current streak
            if row['summonerName'] == curr_summoner and streak_going:
                if latest_game:
                    streak_win = row['win']
                    latest_game = False
                if streak_win == row['win']:
                    streak_len += 1
                else:
                    streak_going = False
        if 'gameInfo' not in ten_match_detail:
            ten_match_detail['gameInfo'] = [game_info]
        else:
            ten_match_detail['gameInfo'].append(game_info)
        if 'part' not in ten_match_detail:
            ten_match_detail['part'] = [participants]
        else:
            ten_match_detail['part'].append(participants)
       

             
    return ten_match_detail, streak_win, streak_len

### Updates database to reflect user's new search history
def update_database(username, summoner_name, region):
    entry_exists = SearchHistory.objects.filter(uid=username)
    current_entry = summoner_name + ',' + region
    
    if not entry_exists:
        ## Create new database entry if first time user
        new_history = SearchHistory.objects.create(uid=username, history=current_entry)
        new_history.save()
        return
    
    history_entry = SearchHistory.objects.get(uid=username)
    history = history_entry.history.split(';')
    
    # Get index of current entry in history; -1 if not present
    current_entry_idx = -1
    for i in range(len(history)):
        if history[i] == current_entry:
            current_entry_idx = i
            
    if current_entry_idx > -1:
        # If current entry is found, move it up to the front,
        # shifting elements back as needed
        temp = history[current_entry_idx]
        while current_entry_idx > 0:
            history[current_entry_idx] = history[current_entry_idx - 1]
            current_entry_idx -= 1
        history[0] = temp
    else:
        # If current entry is not found, add it to the front
        history = [current_entry] + history
        
    ## Limit database size to 5 entries
    if len(history) >= 6:
        history.pop()
    
    history_entry.history = ';'.join(history)
    history_entry.save()

    #HTML/CSS
    def style(request):
       return render(request,'style.css')


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
        api_key = 'RGAPI-2df33002-8998-4de1-bbce-c62b60f8dc96'
        watcher = LolWatcher(api_key)
        me = watcher.summoner.by_name(my_region, name)
        me = me['id']
        ranked_stats = watcher.league.by_summoner(my_region, me)
        name = ranked_stats[0]['summonerName']
        rank, tier = ranked_stats[0]['rank'], ranked_stats[0]['tier'] 
        rankTier =  tier +rank 
        #
       

     


        
        #name = name[summonerName]

 
        return render(request, 'display.html', {'response': ranked_stats, 'name': name, 'rank':rankTier})
        #if form.is_valid():
           # name = form.cleaned_data['your_name']
            #region = form.cleaned_data['your_region'] 
    else:
        form = NameForm()
        return render(request, "data.html", {"form":form})


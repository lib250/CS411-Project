from django.shortcuts import render, redirect
from django.http import  HttpResponse, HttpResponseRedirect
import requests 
from django.template import loader
from riotwatcher import LolWatcher, ApiError
import pandas as pd
# Create your views here.
from .forms import NameForm
def index(request):
    template = loader.get_template('input.html')

    return  HttpResponse(template.render())
#RGAPI-41cbb789-b621-4522-acef-e5211ecfc836
#Regions, inputted lower case
#EUN1, EUW1	JP1	KR	LA1	LA2 NA1	OC1	TR1	RU BR1
def ritoAPI(request):
    api_key = 'RGAPI-41cbb789-b621-4522-acef-e5211ecfc836'
    watcher = LolWatcher(api_key)
    form = NameForm(request.POST)
    name = form.cleaned_data['your_name']
    my_region = form.cleaned_data['your_region']
    me = watcher.summoner.by_name(my_region, name)
    ranked_stats = watcher.league.by_summoner(my_region, me['id'])
    return render(request, 'display.html', {'response': ranked_stats})

def get_summoner(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        
        form.save()
       # full = NameForm(your_name = name, your_region = region)
       
        return redirect('/autho/data')
        #if form.is_valid():
           # name = form.cleaned_data['your_name']
            #region = form.cleaned_data['your_region'] 
    else:
        form = NameForm()
        return render(request, "data.html", {"form":form})


﻿"""
Definition of views.
"""
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from app.models import Sources, Sectors, Stocks, Tweeter, Opinion, CorrectionData, StocksPrices, LabledCounter, StockCounter, RelevancyCounter, SentimentCounter, DailyPrices, WeeklyPrices, UserCounter, Evaluation, PredictionCounter, Correction, Matrix
from django.utils import timezone
from Filter.Filter import Filter
from bs4 import BeautifulSoup
from django.db.models import Sum
from random import randint
from dateutil.relativedelta import relativedelta
from django.forms.models import model_to_dict
import urllib
import json
from TwitterCrawler.TwitterCrawler import *
import os
import threading
import django_crontab
#from pytz import timezone
from dateutil.parser import parse
from requests_oauthlib import OAuth1
import requests
import urllib.parse as urllib_parse
from twitter import *
import re
import gc
import subprocess
from django.http import HttpResponse, JsonResponse
from Filter import FilterStocks
from django.db.models import Max, Min
import copy



request_token_url = 'https://api.twitter.com/oauth/request_token'
access_url = 'https://api.twitter.com/oauth/access_token'
authenticate_url = 'https://api.twitter.com/oauth/authenticate'
base_authorization_url = 'https://api.twitter.com/oauth/authorize'

consumerKey="xNRGvHoz9L4xKGP28m7qbg"
consumerSecret="oFv4dhBekboNg7pKa2BS0zztHqusr91SIdmKErDaycI"
accessToken="1846277677-36dTObVu6LfVDSuU72M3HCTCv2g50dYoTxzuAOZ"
accessTokenSecret="Yu4lZdbebuO3tpof6xYzi4Qy7HZL4aL3YQiCYgsro"
resource_owner_key = ""
resource_owner_secret = ""


class NewsItem:
    title = ""
    link = ""
    pubDate = ""
    
def isNumber(value):
    try:
        float(value)
        return True
    except ValueError:
        return False 
    
    
@ajax
def get_stocks_weights(request):
    content_return = []
    for stocks in Stocks.objects.exclude(stock_id__in=[1,2,4,5]).select_related('sector'):
        try:
            weight = StockCounter.objects.filter(stock=stocks.stock).aggregate(Sum('counter'))['counter__sum']
        except:
            weight = 0
        sector = stocks.sector.sector
        content_return.append({'text':stocks.stock, 'weight':weight,'html':{'class':sector}})

    return content_return

    
def index(request):
    """Renders the home page."""
    if 'message' in request.session:
        message = request.session['message']
        del request.session['message']
    if 'error' in request.session:
        message = request.session['error']
        del request.session['error']

    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        context_instance = RequestContext(request,
        {
            'title':'Home Page',
            'message': message if 'message' in locals() else "",
            'error': message if 'error' in locals() else "",
        })
    )

def index_proto(request):
    """Renders the home page."""
    if 'message' in request.session:
        message = request.session['message']
        del request.session['message']
    if 'error' in request.session:
        message = request.session['error']
        del request.session['error']

    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index_proto.html',
        context_instance = RequestContext(request,
        {
            'title':'Home Page',
            'message': message if 'message' in locals() else "",
            'error': message if 'error' in locals() else "",
        })
    )


#@login_required
def home(request):
    '''
    from twython import Twython
    global twitter
    twitter = Twython("MGMeNEK5bEqADjJRDJmQ8Yy1f", "eVR1kjrTdHPEiFuLoAEA6pPGSnuZ1NnAa1EwtqBi4wVA1tbRHo", "91079548-uhlRrwtgVQcavlf3lv4Dy1ZFCq5CXvBQFvc5A1l0n", "V6vLsqzqrdfs2YX4I1NVG2gP845gjTrBSDNxHVz496g66")
    '''
    if(request.user.is_authenticated()):
        # Start the TwitterCrawler      
        PROJECT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
        configFileCrawler = os.path.join(PROJECT_DIR, 'TwitterCrawler','Configurations', 'Configurations.xml')
        global twitterCrawler
        twitterCrawler = TwitterCrawler(configFileCrawler, None, None, None)
        #results = twitterCrawler.SearchQueryAPI(query, -1, -1)
    
        return render(
            request,
            'app/home.html',
            context_instance = RequestContext(request,
            {
                'title':'Home',
                #'tweets': tweets,
            })
        )
    else:
        return redirect('/register')

#@login_required
def home_proto(request):
    '''
    from twython import Twython
    global twitter
    twitter = Twython("MGMeNEK5bEqADjJRDJmQ8Yy1f", "eVR1kjrTdHPEiFuLoAEA6pPGSnuZ1NnAa1EwtqBi4wVA1tbRHo", "91079548-uhlRrwtgVQcavlf3lv4Dy1ZFCq5CXvBQFvc5A1l0n", "V6vLsqzqrdfs2YX4I1NVG2gP845gjTrBSDNxHVz496g66")
    '''
    try:
        if(request.session.get('user_authenticated')):
        
            # Start the TwitterCrawler      
            PROJECT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
            configFileCrawler = os.path.join(PROJECT_DIR, 'TwitterCrawler','Configurations', 'Configurations.xml')
            global twitterCrawler
            twitterCrawler = TwitterCrawler(configFileCrawler, None, None, None)
            #results = twitterCrawler.SearchQueryAPI(query, -1, -1)
        
            return render(
                request,
                'app/home_proto.html',
                context_instance = RequestContext(request,
                {
                    'title':'Home',
                    #'tweets': tweets,
                })
            )
    
        else:
            return redirect('/prototype')
    except:
        return redirect('/prototype')

#@login_required
def home_filtered(request):
    '''
    from twython import Twython
    global twitter
    twitter = Twython("MGMeNEK5bEqADjJRDJmQ8Yy1f", "eVR1kjrTdHPEiFuLoAEA6pPGSnuZ1NnAa1EwtqBi4wVA1tbRHo", "91079548-uhlRrwtgVQcavlf3lv4Dy1ZFCq5CXvBQFvc5A1l0n", "V6vLsqzqrdfs2YX4I1NVG2gP845gjTrBSDNxHVz496g66")
    '''
    # Start the TwitterCrawler      
    PROJECT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    configFileCrawler = os.path.join(PROJECT_DIR, 'TwitterCrawler','Configurations', 'Configurations.xml')
    global twitterCrawler
    twitterCrawler = TwitterCrawler(configFileCrawler, None, None, None)
    #results = twitterCrawler.SearchQueryAPI(query, -1, -1)

    return render(
        request,
        'app/home_filtered.html',
        context_instance = RequestContext(request,
        {
            'title':'Home filtered',
            #'tweets': tweets,
        })
    )

def home_training(request):
    return render(
        request,
        'app/training.html',
        context_instance = RequestContext(request,
        {
            'title':'Training',
            #'tweets': tweets,
        })
    )

def profile(request,arg):
    return render(
        request,
        'app/profile.html',
        context_instance = RequestContext(request,
        {
            'title': arg,
        })
    )


def test123(request):
    return render(
        request,
        'app/test123.html',
        context_instance = RequestContext(request,
        {
            'title':'Training',
            #'tweets': tweets,
        })
    )

def home_statistics(request):
    return render(
        request,
        'app/statistics.html',
        context_instance = RequestContext(request,
        {
            'title':'Statistics',
            #'tweets': tweets,
        })
    )

@ajax
def p_table(request):
    day = request.POST['day']
    print(day)
    if day == '':
        day = datetime.datetime.strftime(timezone.now() + datetime.timedelta(hours=8) + datetime.timedelta(hours=3),"%Y-%m-%d")
        # 8 because the day ends at 4 PM and 3 for the timezone differenece 

    prediction_object = PredictionCounter.objects.filter(day=day);
    content_return = {}
    content_return['tab'] = {}

    for stock_object in Stocks.objects.exclude(stock_id__in=[1,2,4,5]).select_related('sector').order_by('id'):
        content_return['tab'][stock_object.id] = {}
        content_return['tab'][stock_object.id]['stock'] = stock_object.stock
        content_return['tab'][stock_object.id]['sector'] = stock_object.sector.sector
        content_return['tab'][stock_object.id]['r'] = {}
        content_return['tab'][stock_object.id]['s'] = {}
        content_return['tab'][stock_object.id]['q'] = {}
        try:
            content_return['tab'][stock_object.id]['r']['relevant'] = prediction_object.filter(classifier='r').filter(stock=stock_object.stock).filter(prediction='relevant')[0].counter
        except:
            content_return['tab'][stock_object.id]['r']['relevant'] = 0
        try: 
            content_return['tab'][stock_object.id]['r']['irrelevant'] = prediction_object.filter(classifier='r').filter(stock=stock_object.stock).filter(prediction='irrelevant')[0].counter
        except:
            content_return['tab'][stock_object.id]['r']['irrelevant'] = 0 
        try: 
            content_return['tab'][stock_object.id]['r']['Uncertain'] = prediction_object.filter(classifier='r').filter(stock=stock_object.stock).filter(prediction='Uncertain')[0].counter
        except:
            content_return['tab'][stock_object.id]['r']['Uncertain'] = 0  

        try:
            content_return['tab'][stock_object.id]['s']['positive'] = prediction_object.filter(classifier='s').filter(stock=stock_object.stock).filter(prediction='positive')[0].counter
        except:
            content_return['tab'][stock_object.id]['s']['positive'] = 0
        try:
            content_return['tab'][stock_object.id]['s']['negative'] = prediction_object.filter(classifier='s').filter(stock=stock_object.stock).filter(prediction='negative')[0].counter
        except:
            content_return['tab'][stock_object.id]['s']['negative'] = 0
        try:
            content_return['tab'][stock_object.id]['s']['neutral'] = prediction_object.filter(classifier='s').filter(stock=stock_object.stock).filter(prediction='neutral')[0].counter
        except:
            content_return['tab'][stock_object.id]['s']['neutral'] = 0

        try:
            content_return['tab'][stock_object.id]['q']['question'] = prediction_object.filter(classifier='q').filter(stock=stock_object.stock).filter(prediction=1)[0].counter
        except:
            content_return['tab'][stock_object.id]['q']['question'] = 0
        try:
            content_return['tab'][stock_object.id]['q']['notaquestion'] = prediction_object.filter(classifier='q').filter(stock=stock_object.stock).filter(prediction=0)[0].counter
        except:
            content_return['tab'][stock_object.id]['q']['notaquestion'] = 0

    content_return['tot'] = {}
    content_return['tot']['rr'] = PredictionCounter.objects.filter(day=day).filter(classifier='r').filter(prediction='relevant').aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['ri'] = PredictionCounter.objects.filter(day=day).filter(classifier='r').filter(prediction='irrelevant').aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['ru'] = PredictionCounter.objects.filter(day=day).filter(classifier='r').filter(prediction='uncertain').aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['sp'] = PredictionCounter.objects.filter(day=day).filter(classifier='s').filter(prediction='positive').aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['sn'] = PredictionCounter.objects.filter(day=day).filter(classifier='s').filter(prediction='negative').aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['su'] = PredictionCounter.objects.filter(day=day).filter(classifier='s').filter(prediction='neutral').aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['qq'] = PredictionCounter.objects.filter(day=day).filter(classifier='q').filter(prediction='question').aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['qr'] = PredictionCounter.objects.filter(day=day).filter(classifier='q').filter(prediction='reply').aggregate(Sum('counter'))['counter__sum'] or 0

    return content_return 

@ajax
def h_table(request):
    s_id = request.POST['s_id']
    content_return = {}
    stock_name = Stocks.objects.filter(id=s_id)[0].stock
    prediction_object = PredictionCounter.objects.filter(stock=stock_name);
    #start_date = timezone.now()
    start_date = timezone.now() + timedelta(hours=8) + timedelta(hours=3)

    counter = 0
    for single_date in (start_date - timedelta(n) for n in range(420)):
        day=datetime.datetime.strftime(single_date,"%Y-%m-%d");
        content_return[day] = {}
        content_return[day]['stock'] = stock_name
        #content_return[day]['day'] = str(counter) + '_' + str(day)
        content_return[day]['day'] = day
        content_return[day]['r'] = {}
        content_return[day]['s'] = {}
        content_return[day]['q'] = {}
        counter += 1;

        if s_id != "5":
            try:
                content_return[day]['r']['relevant'] = prediction_object.filter(classifier='r').filter(day=day).filter(prediction='relevant')[0].counter
            except:
                content_return[day]['r']['relevant'] = 0
            try:
                content_return[day]['r']['irrelevant'] = prediction_object.filter(classifier='r').filter(day=day).filter(prediction='irrelevant')[0].counter
            except:
                content_return[day]['r']['irrelevant'] = 0
            try:
                content_return[day]['r']['Uncertain'] = prediction_object.filter(classifier='r').filter(day=day).filter(prediction='Uncertain')[0].counter
            except:
                content_return[day]['r']['Uncertain'] = 0
            try:
                content_return[day]['s']['positive'] = prediction_object.filter(classifier='s').filter(day=day).filter(prediction='positive')[0].counter
            except:
                content_return[day]['s']['positive'] = 0
            try:
                content_return[day]['s']['negative'] = prediction_object.filter(classifier='s').filter(day=day).filter(prediction='negative')[0].counter
            except:
                content_return[day]['s']['negative'] = 0
            try:
                content_return[day]['s']['neutral'] = prediction_object.filter(classifier='s').filter(day=day).filter(prediction='neutral')[0].counter
            except:
                content_return[day]['s']['neutral'] = 0
            try:
                content_return[day]['q']['question'] = prediction_object.filter(classifier='q').filter(day=day).filter(prediction=1)[0].counter
            except:
                content_return[day]['q']['question'] = 0
            try:
                content_return[day]['q']['notaquestion'] = prediction_object.filter(classifier='q').filter(day=day).filter(prediction=0)[0].counter
            except:
                content_return[day]['q']['notaquestion'] = 0
        else:
            prediction_object = PredictionCounter.objects.filter(day=day)
            content_return[day]['r']['relevant'] = prediction_object.filter(classifier='r').filter(prediction='relevant').aggregate(Sum('counter'))['counter__sum'] or 0 
            content_return[day]['r']['irrelevant'] = prediction_object.filter(classifier='r').filter(prediction='irrelevant').aggregate(Sum('counter'))['counter__sum'] or 0
            content_return[day]['r']['Uncertain'] = prediction_object.filter(classifier='r').filter(prediction='Uncertain').aggregate(Sum('counter'))['counter__sum'] or 0
            content_return[day]['s']['positive'] = prediction_object.filter(classifier='s').filter(prediction='positive').aggregate(Sum('counter'))['counter__sum'] or 0
            content_return[day]['s']['negative'] = prediction_object.filter(classifier='s').filter(prediction='negative').aggregate(Sum('counter'))['counter__sum'] or 0
            content_return[day]['s']['neutral'] = prediction_object.filter(classifier='s').filter(prediction='neutral').aggregate(Sum('counter'))['counter__sum'] or 0
            content_return[day]['q']['question'] = prediction_object.filter(classifier='q').filter(prediction=1).aggregate(Sum('counter'))['counter__sum'] or 0
            content_return[day]['q']['notaquestion'] = prediction_object.filter(classifier='q').filter(prediction=0).aggregate(Sum('counter'))['counter__sum'] or 0
    return content_return

@ajax
def c_table(request):
    segment = request.POST['segment']
    if segment == '':
        segment = 1

    content_return = {}
    content_return['tab'] = {}
    tot_completed_segments = 0
    r_correct_counter = 0;
    r_incorrect_counter = 0;
    s_correct_counter = 0;
    s_incorrect_counter = 0;
    q_correct_counter = 0;
    q_incorrect_counter = 0;

    for stock_object in Stocks.objects.exclude(stock_id__in=[1,2,4,5]).select_related('sector').order_by('id'):
        segment_r = Correction.objects.filter(stock_id=stock_object.stock_id).filter(classifier='r').aggregate(Max('segment'))['segment__max'] or 1
        segment_s = Correction.objects.filter(stock_id=stock_object.stock_id).filter(classifier='s').aggregate(Max('segment'))['segment__max'] or 1
        segment_q = Correction.objects.filter(stock_id=stock_object.stock_id).filter(classifier='q').aggregate(Max('segment'))['segment__max'] or 1
        correction_object_r = Correction.objects.filter(segment=segment_r);
        correction_object_s = Correction.objects.filter(segment=segment_s);
        correction_object_q = Correction.objects.filter(segment=segment_q);

        content_return['tab'][stock_object.id] = {}
        content_return['tab'][stock_object.id]['stock'] = stock_object.stock
        content_return['tab'][stock_object.id]['sector'] = stock_object.sector.sector
        content_return['tab'][stock_object.id]['completed_segment'] = segment_r - 1;
        content_return['tab'][stock_object.id]['r'] = {}
        content_return['tab'][stock_object.id]['s'] = {}
        content_return['tab'][stock_object.id]['q'] = {}
        try:
            content_return['tab'][stock_object.id]['r']['correct'] = correction_object_r.filter(classifier='r').filter(stock_id=stock_object.stock_id).filter(correction=1)[0].counter
        except:
            content_return['tab'][stock_object.id]['r']['correct'] = 0
        try: 
            content_return['tab'][stock_object.id]['r']['incorrect'] = correction_object_r.filter(classifier='r').filter(stock_id=stock_object.stock_id).filter(correction=0)[0].counter
        except:
            content_return['tab'][stock_object.id]['r']['incorrect'] = 0 

        try:
            content_return['tab'][stock_object.id]['s']['correct'] = correction_object_s.filter(classifier='s').filter(stock_id=stock_object.stock_id).filter(correction=1)[0].counter
        except:
            content_return['tab'][stock_object.id]['s']['correct'] = 0
        try:
            content_return['tab'][stock_object.id]['s']['incorrect'] = correction_object_s.filter(classifier='s').filter(stock_id=stock_object.stock_id).filter(correction=0)[0].counter
        except:
            content_return['tab'][stock_object.id]['s']['incorrect'] = 0

        try:
            content_return['tab'][stock_object.id]['q']['correct'] = correction_object_q.filter(classifier='q').filter(stock_id=stock_object.stock_id).filter(correction=1)[0].counter
        except:
            content_return['tab'][stock_object.id]['q']['correct'] = 0
        try:
            content_return['tab'][stock_object.id]['q']['incorrect'] = correction_object_q.filter(classifier='q').filter(stock_id=stock_object.stock_id).filter(correction=0)[0].counter
        except:
            content_return['tab'][stock_object.id]['q']['incorrect'] = 0

        r_correct_counter += content_return['tab'][stock_object.id]['r']['correct']
        r_incorrect_counter += content_return['tab'][stock_object.id]['r']['incorrect']
        s_correct_counter += content_return['tab'][stock_object.id]['s']['correct']
        s_incorrect_counter += content_return['tab'][stock_object.id]['s']['incorrect']
        q_correct_counter += content_return['tab'][stock_object.id]['q']['correct']
        q_incorrect_counter += content_return['tab'][stock_object.id]['q']['incorrect']
        tot_completed_segments += content_return['tab'][stock_object.id]['completed_segment'];

    content_return['tot'] = {}
    content_return['tot']['rc'] = r_correct_counter
    content_return['tot']['ri'] = r_incorrect_counter
    content_return['tot']['sc'] = s_correct_counter
    content_return['tot']['si'] = s_incorrect_counter
    content_return['tot']['qc'] = q_correct_counter
    content_return['tot']['qi'] = q_incorrect_counter
    content_return['tot']['tot_completed_segments'] = tot_completed_segments
    return content_return 

@ajax
def ch_table(request):
    s_id = request.POST['s_id']
    print(s_id)
    stock_name = Stocks.objects.filter(id=s_id)[0].stock
    stock_id = Stocks.objects.filter(id=s_id)[0].stock_id
    correction_object = Correction.objects.filter(stock_id=stock_id);
    max_segment = correction_object.aggregate(Max('segment'))['segment__max'] or 0;

    print(max_segment)
    content_return = {}
    content_return['tab'] = {}

    for segment in range(1,max_segment+1):
        content_return['tab'][segment] = {}
        content_return['tab'][segment]['stock'] = stock_name
        content_return['tab'][segment]['r'] = {}
        content_return['tab'][segment]['s'] = {}
        content_return['tab'][segment]['q'] = {}
        try:
            content_return['tab'][segment]['r']['correct'] = correction_object.filter(classifier='r').filter(segment=segment).filter(correction=1)[0].counter
        except:
            content_return['tab'][segment]['r']['correct'] = 0
        try:
            content_return['tab'][segment]['r']['incorrect'] = correction_object.filter(classifier='r').filter(segment=segment).filter(correction=0)[0].counter
        except:
            content_return['tab'][segment]['r']['incorrect'] = 0
        try:
            content_return['tab'][segment]['s']['correct'] = correction_object.filter(classifier='s').filter(segment=segment).filter(correction=1)[0].counter
        except:
            content_return['tab'][segment]['s']['correct'] = 0
        try: 
            content_return['tab'][segment]['s']['incorrect'] = correction_object.filter(classifier='s').filter(segment=segment).filter(correction=0)[0].counter
        except:
            content_return['tab'][segment]['s']['incorrect'] = 0
        try:
            content_return['tab'][segment]['q']['correct'] = correction_object.filter(classifier='q').filter(segment=segment).filter(correction=1)[0].counter
        except:
            content_return['tab'][segment]['q']['correct'] = 0
        try: 
            content_return['tab'][segment]['q']['incorrect'] = correction_object.filter(classifier='q').filter(segment=segment).filter(correction=0)[0].counter
        except:
            content_return['tab'][segment]['q']['incorrect'] = 0
        content_return['tab'][segment]['r']['stock_count'] = correction_object.filter(classifier='r').filter(segment=segment+1).aggregate(Max('stock_count'))['stock_count__max'] or 0;
        content_return['tab'][segment]['s']['stock_count'] = correction_object.filter(classifier='s').filter(segment=segment+1).aggregate(Max('stock_count'))['stock_count__max'] or 0;
        content_return['tab'][segment]['q']['stock_count'] = correction_object.filter(classifier='q').filter(segment=segment+1).aggregate(Max('stock_count'))['stock_count__max'] or 0;

    #content_return['tab'][segment]['q']['stock_count'] = 0
    content_return['tot'] = {}
    content_return['tot']['rc'] = correction_object.filter(classifier='r').filter(correction=1).aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['ri'] = correction_object.filter(classifier='r').filter(correction=0).aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['sc'] = correction_object.filter(classifier='s').filter(correction=1).aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['si'] = correction_object.filter(classifier='s').filter(correction=0).aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['qc'] = correction_object.filter(classifier='q').filter(correction=1).aggregate(Sum('counter'))['counter__sum'] or 0
    content_return['tot']['qi'] = correction_object.filter(classifier='q').filter(correction=0).aggregate(Sum('counter'))['counter__sum'] or 0
    return content_return 

@ajax
def get_prices_line(request):
    stock_name = request.POST['query']
    content_return = {}
    prices = DailyPrices.objects.filter(stock=stock_name).values()
    content_return = [];
    for price in prices:
        l=price['concat'].split(',')
        close=l[0]
        content_return.append([price['day'],float(close)]);

    return content_return[-50:];

@ajax
def get_prices_candle(request):
    stock_name = request.POST['query']
    print("Start get_prices_candle")
    content_return = {}
    prices = DailyPrices.objects.filter(stock=stock_name).values()
    content_return = [];
    for price in prices:
        l=price['concat'].split(',')
        close=l[0]
        open=l[-1]
        #print(price['day'])
        #print(price['min'])
        #print(price['max'])
        #print(open)
        #print(close)
        content_return.append([price['day'],float(price['min']),float(open),float(close),float(price['max']),'<b>'+price['day']+'</b>   O:'+open+' H:'+price['max']+' L:'+price['min']+' C:'+close]);
    print("End get_prices_candle")
    return content_return[-50:];

@ajax
def get_stock_volume(request):
    stock_name = request.POST['query']
    content_return = []
    print("Start get_stock_volume")
    now_time = timezone.now()
    start_point = timezone.datetime(now_time.year, now_time.month, now_time.day, 8, 0, 0,)
    graph_point = start_point
    end_point = timezone.datetime(now_time.year, now_time.month, now_time.day, 17, 0, 0,)
    one_hour = timezone.timedelta(hours=1)
    stock_id = Stocks.objects.filter(stock=stock_name)[0].stock_id
    all_tweets = Opinion.objects.filter(stock=stock_id).exclude(created_at=None).values().order_by('-id')
    while(graph_point <= end_point):
        prev_graph_point = graph_point
        graph_point += one_hour
        
        w = count_number_tweets_in_range(all_tweets, prev_graph_point, graph_point)
        # FIX: convert the prev_graph_point into the Saudi timezone. See http://stackoverflow.com/questions/1398674/python-display-the-time-in-a-different-time-zone
        # All timezones names can be found at: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        # Saudi is: 'Asia/Riyadh'
        content_return.append([{'v':[prev_graph_point.hour,0,0],'f':str(prev_graph_point.hour)}, w])

    print("End get_stock_volume")
    return content_return;

def date_hour(created_at):
   return int(created_at.strftime('%H'));

@ajax
def get_hours_distribution(request):
    tweeter_sname = request.POST['tweeter_sname']
    period = request.POST['period']
    tweeter = Tweeter.objects.filter(tweeter_sname=tweeter_sname)[0]
    tweeter_id = tweeter.tweeter_id
    from itertools import groupby
    if period == "alltime":
        start_time="2000-01-01";
    elif period == "1w":
        start_time=datetime.datetime.strftime(timezone.now()-relativedelta(weeks=+1),"%Y-%m-%d")
    elif period == "2w":
        start_time=datetime.datetime.strftime(timezone.now()-relativedelta(weeks=+2),"%Y-%m-%d")
    elif period == "1m":
        start_time=datetime.datetime.strftime(timezone.now()-relativedelta(months=+1),"%Y-%m-%d")
    elif period == "3m":
        start_time=datetime.datetime.strftime(timezone.now()-relativedelta(months=+3),"%Y-%m-%d")
        
    all_tweets = Opinion.objects.filter(tweeter_id=tweeter_id).filter(created_at__gte=start_time).values('created_at').order_by('-id')
    arr = [None] * len(all_tweets)
    for x in range(0,len(all_tweets)):
        arr[x]=date_hour(all_tweets[x]['created_at']+timezone.timedelta(hours=3))
    valdict = dict((k, len(list(g))) for k, g in groupby(sorted(arr)))
    content_return = []; 
    for x in range(0,24):
        try:
            count=valdict[x]
        except:
            count=0
        content_return.append([{'v':[x,0,0],'f':str(x)}, count]);

    content_return.append([{'v':[24,0,0],'f':str(24)}, content_return[0][1] ]);
    return content_return;

@ajax
def get_stacked_sentiment(request):
    tweeter_sname = request.POST['tweeter_sname']
    period = request.POST['period']
    tweeter = Tweeter.objects.filter(tweeter_sname=tweeter_sname)[0]
    tweeter_id = tweeter.tweeter_id
    tweeter = Tweeter.objects.filter(tweeter_sname=tweeter_sname)[0]
    tweeter_id = tweeter.tweeter_id
    from itertools import groupby
    if period == "alltime":
        start_time="2000-01-01";
    elif period == "1w":
        start_time=datetime.datetime.strftime(timezone.now()-relativedelta(weeks=+1),"%Y-%m-%d")
    elif period == "2w":
        start_time=datetime.datetime.strftime(timezone.now()-relativedelta(weeks=+2),"%Y-%m-%d")
    elif period == "1m":
        start_time=datetime.datetime.strftime(timezone.now()-relativedelta(months=+1),"%Y-%m-%d")
    elif period == "3m":
        start_time=datetime.datetime.strftime(timezone.now()-relativedelta(months=+3),"%Y-%m-%d")
    
    all_tweets = Opinion.objects.filter(tweeter_id=tweeter_id).filter(created_at__gte=start_time).filter(p_sentiment__isnull=False).values('p_sentiment','stock_id')
    arr_s = [None] * len(all_tweets)
    for x in range(0,len(all_tweets)):
        arr_s[x]=all_tweets[x]['stock_id']
    valdict = dict((k, len(list(g))) for k, g in groupby(sorted(arr_s)))
    arr_s2 = sorted(valdict, key=valdict.get, reverse=True)
    arr_stock=[0,0,0,0,0]
    content_return=[];
    for x in range(0,min(5,len(arr_s2))):
        try:
            arr_stock[x]=arr_s2[x]
            all_tweets_by_stock = all_tweets.filter(stock_id=arr_stock[x])
            arr_p = [None] * len(all_tweets_by_stock)
            for n in range(0,len(all_tweets_by_stock)):
                arr_p[n]=all_tweets_by_stock[n]['p_sentiment']
            valdict2 = dict((k, len(list(g))) for k, g in groupby(sorted(arr_p)))
        except:
            pass 
        try:
            pos = valdict2['positive']
        except:
            pos = 0
        try:
            neg = valdict2['negative']
        except:
            neg = 0
        try:
            neu = valdict2['neutral']
        except:
            neu = 0
        content_return.append([Stocks.objects.filter(stock_id=arr_s2[x])[0].stock,pos,neg,neu]);
    return content_return;
    
@ajax
def get_stock_col_rel_info(request):
    stock_name = request.POST['query']
    content_return = []
    print("Start get_stock_col_rel_info")
    now_time = timezone.now()
    start_point = timezone.datetime(now_time.year, now_time.month, now_time.day, 8, 0, 0,)
    graph_point = start_point
    end_point = timezone.datetime(now_time.year, now_time.month, now_time.day, 17, 0, 0,)
    one_hour = timezone.timedelta(hours=1)
    stock_id = Stocks.objects.filter(stock=stock_name)[0].stock_id
    rel_tweets = Opinion.objects.filter(stock=stock_id, voted_relevancy='Relevant').values().order_by('-id')
    irrel_tweets = Opinion.objects.filter(stock=stock_id, voted_relevancy='Irrelevant').values().order_by('-id')
    while(graph_point <= end_point):
        prev_graph_point = graph_point
        graph_point += one_hour
        
        rel_count = count_number_tweets_in_range(rel_tweets, prev_graph_point, graph_point)
        irrel_count = count_number_tweets_in_range(irrel_tweets, prev_graph_point, graph_point)
        # FIX: convert the prev_graph_point into the Saudi timezone. See http://stackoverflow.com/questions/1398674/python-display-the-time-in-a-different-time-zone
        # All timezones names can be found at: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        # Saudi is: 'Asia/Riyadh'
        content_return.append([{'v':[prev_graph_point.hour,0,0],'f':str(prev_graph_point.hour)}, rel_count, irrel_count])

    print("End get_stock_col_rel_info")
    return content_return;

@ajax
def get_stock_col_sent_info(request):
    stock_name = request.POST['query']
    content_return = []
    print("Start get_stock_col_sent_info")
    now_time = timezone.now()
    start_point = timezone.datetime(now_time.year, now_time.month, now_time.day, 8, 0, 0,)
    graph_point = start_point
    end_point = timezone.datetime(now_time.year, now_time.month, now_time.day, 17, 0, 0,)
    one_hour = timezone.timedelta(hours=1)
    stock_id = Stocks.objects.filter(stock=stock_name)[0].stock_id
    pos_tweets = Opinion.objects.filter(stock=stock_id, voted_sentiment='Positive').values().order_by('-id')
    neg_tweets = Opinion.objects.filter(stock=stock_id, voted_sentiment='Negative').values().order_by('-id')
    neu_tweets = Opinion.objects.filter(stock=stock_id, voted_sentiment='Neutral').values().order_by('-id')
    while(graph_point <= end_point):
        prev_graph_point = graph_point
        graph_point += one_hour
        
        pos_count = count_number_tweets_in_range(pos_tweets, prev_graph_point, graph_point)
        neg_count = count_number_tweets_in_range(neg_tweets, prev_graph_point, graph_point)
        neu_count = count_number_tweets_in_range(neu_tweets, prev_graph_point, graph_point)
        # FIX: convert the prev_graph_point into the Saudi timezone. See http://stackoverflow.com/questions/1398674/python-display-the-time-in-a-different-time-zone
        # All timezones names can be found at: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        # Saudi is: 'Asia/Riyadh'
        content_return.append([{'v':[prev_graph_point.hour,0,0],'f':str(prev_graph_point.hour)}, pos_count, neg_count, neu_count])

    print("End get_stock_col_sent_info")
    return content_return;

@ajax
def get_overall_rel_info(request):

    content_return = []
    print("Start get_overall_rel_info")
    #all_tweets = Opinion.objects.filter(stock=stock_name).values().order_by('-id')
    try:
        rel_count = RelevancyCounter.objects.extra(where={"`relevancy` = 'relevant' "}).values()[0]['counter']
    except:
        rel_count = 10
    try:
        irrel_count = RelevancyCounter.objects.extra(where={"`relevancy` = 'irrelevant' "}).values()[0]['counter']
    except:
        irrel_count = 10
    
    content_return.append(['Relevant', rel_count])
    content_return.append(['Irrelevant', irrel_count])
    print("End get_overall_rel_info")

    return content_return;
@ajax
def get_overall_sent_info(request):
    content_return = []
    #all_tweets = Opinion.objects.filter(stock=stock_name).values().order_by('-id')
    print("Start get_overall_sent_info")
    try:
        pos_count = SentimentCounter.objects.extra(where={"`sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        pos_count = 10
    try:
        neg_count = SentimentCounter.objects.extra(where={"`sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        neg_count = 10
    try:
        neu_count = SentimentCounter.objects.extra(where={"`sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        neu_count = 10
    
    content_return.append(['Positive', pos_count])
    content_return.append(['Negative', neg_count])
    content_return.append(['Neutral', neu_count])

    print("End get_overall_sent_info")
    return content_return;  

@ajax
def get_stock_rel_info(request):
    stock_name = request.POST['query']
    content_return = []
    print("Start get_stock_rel_info")
    #all_tweets = Opinion.objects.filter(stock=stock_name).values().order_by('-id')
    try:
        rel_count = RelevancyCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `relevancy` = 'relevant' "}).values()[0]['counter']
    except:
        rel_count = 10
    try:
        irrel_count = RelevancyCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `relevancy` = 'irrelevant' "}).values()[0]['counter']
    except:
        irrel_count = 10
    
    content_return.append(['Relevant', rel_count])
    content_return.append(['Irrelevant', irrel_count])
    print("End get_stock_rel_info")

    return content_return;

@ajax
def get_stock_sent_info(request):
    stock_name = request.POST['query']
    content_return = []
    print("Start get_stock_sent_info")

    #all_tweets = Opinion.objects.filter(stock=stock_name).values().order_by('-id')
    try:
        pos_count = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        pos_count = 10
    try:
        neg_count = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        neg_count = 10
    try:
        neu_count = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        neu_count = 10
    
    content_return.append(['Positive', pos_count])
    content_return.append(['Negative', neg_count])
    content_return.append(['Neutral', neu_count])
    print("End get_stock_sent_info")

    return content_return;    

def count_number_tweets_in_range(all_tweets, prev_graph_point, graph_point):
    w = 0
    for tweet in all_tweets:
        #tweet_time_stamp = datetime.datetime.strptime(tweet['pub_date'], '%Y-%m-%d %H:%M:%S.%f+00:00')
        if tweet['created_at'] != None:
            tweet_time_stamp = tweet['created_at'].replace(tzinfo=None)
        else:
            tweet_time_stamp = None
        #tweetes_to_render[x].created_at+timedelta(hours=3)
        if((tweet_time_stamp >= prev_graph_point) and (tweet_time_stamp <= graph_point)):
            w += 1
    return w

@ajax
def get_overall_stats(request):
    content_return  = {}
    # Fill in total number of entries in DB for this stock
    # Full DB
    content_return['total_entries_in_DB'] = StockCounter.objects.aggregate(Sum('counter'))['counter__sum']
    if(LabledCounter.objects.aggregate(Sum('counter'))['counter__sum'] != None):
        content_return['total_labeled_entries_in_DB'] = LabledCounter.objects.aggregate(Sum('counter'))['counter__sum']
    else:
        content_return['total_labeled_entries_in_DB'] = 0
    content_return['total_relevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`relevancy` = 'relevant' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_irrelevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`relevancy` = 'irrelevant' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_positive_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_negative_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_neutral_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['user_total_labels_in_DB'] = UserCounter.objects.filter(labeled_user=request.user.username).aggregate(Sum('counter'))['counter__sum']
    return content_return

#@login_required


def runUpdate():
    subprocess.Popen(['sh','/project/DjangoWebProject1_20150924/update_counter.sh']);

@ajax
def update_counters(request):
    d = threading.Thread(target=runUpdate);
    d.start();

@ajax
def get_stock_price(request):
    stock_id = request.POST['s_id']
    content_return = {}
    stock = Stocks.objects.filter(id=stock_id)[0]
    content_return['stock'] = stock.stock
    content_return['full'] = stock.full_name_arabic
    content_return['price'] = StocksPrices.objects.filter(stock=stock.stock_id).order_by('-id')[0].close
    return content_return

@ajax
def get_stock_price_by_id(request):
    stock = request.POST['stock']
    opinion_id = request.POST['opinion_id']
    content_return = {}
    stock = Stocks.objects.filter(stock=stock)[0]
    twitter_id = Opinion.objects.filter(id=opinion_id)[0].twitter_id
    try:
        Op = Opinion.objects.filter(stock=stock.stock_id).filter(twitter_id=twitter_id).select_related('stocksprices')[0]
        content_return['id'] = Op.id
        content_return['old_opinion_id'] = opinion_id
        content_return['price'] = Op.stocksprices.close
    except:
        content_return['id'] = randint(0,9999999)
        content_return['old_opinion_id'] = opinion_id
        content_return['price'] = 'None'
    return content_return

@ajax
def get_tweeter_by_sname(request):
    tweeter_sname = request.POST['tweeter_sname']
    try:
        tweeter = Tweeter.objects.filter(tweeter_sname=tweeter_sname).values()[0]
    except:
        tweeter = 'not_found'
    try:
        tweeter['tweeter_created_at'] = tweeter['tweeter_created_at'].strftime('%b %Y')
    except:
        tweeter['tweeter_created_at'] = "(not available)"

    tweeter['tweeter_location'] = tweeter['tweeter_location'] or ''
    tweeter['tweeter_description'] = tweeter['tweeter_description'] or ''
    tweeter['all_tweets_counter'] = len(Opinion.objects.filter(head_opinion= True).filter(stocksprices_id__isnull=False).filter(source_id=1).filter(tweeter_id=tweeter['tweeter_id']));
    tweeter['retweets_counter'] = len(Opinion.objects.filter(head_opinion= True).filter(stocksprices_id__isnull=False).filter(source_id=1).filter(retweet_original__isnull=False).filter(tweeter_id=tweeter['tweeter_id']));
    tweeter['positive_counter'] = len(Opinion.objects.filter(head_opinion= True).filter(stocksprices_id__isnull=False).filter(source_id=1).filter(p_sentiment='positive').filter(tweeter_id=tweeter['tweeter_id']))
    tweeter['negative_counter'] = len(Opinion.objects.filter(head_opinion= True).filter(stocksprices_id__isnull=False).filter(source_id=1).filter(p_sentiment='negative').filter(tweeter_id=tweeter['tweeter_id']))
    tweeter['neutral_counter'] = len(Opinion.objects.filter(head_opinion= True).filter(stocksprices_id__isnull=False).filter(source_id=1).filter(p_sentiment='neutral').filter(tweeter_id=tweeter['tweeter_id']))
    return tweeter;

@ajax
def get_tweets_by_tweeter(request):
    tweeter_sname = request.POST['tweeter_sname']
    stock_name = request.POST['stock_name']
    start_time = request.POST['start']
    end_time = request.POST['end']
    content_return = {}
    tweeter = Tweeter.objects.filter(tweeter_sname=tweeter_sname)[0]
    tweeter_id = tweeter.tweeter_id
    if stock_name == "none":
        tweetes_to_render=Opinion.objects.filter(head_opinion= True).filter(stocksprices_id__isnull=False).filter(source_id=1).filter(tweeter_id=tweeter_id).select_related('tweeter').select_related('stocksprices')
    else:
        stock_id = Stocks.objects.filter(stock=stock_name)[0].stock_id
        tweetes_to_render=Opinion.objects.filter(head_opinion= True).filter(stocksprices_id__isnull=False).filter(source_id=1).filter(tweeter_id=tweeter_id).filter(stock=stock_id).select_related('tweeter').select_related('stocksprices');
    if start_time == '' and end_time == '':
        tweetes_to_render=list(tweetes_to_render.order_by('-created_at')[0:500]);
    elif start_time != '' and end_time == '':
        tweetes_to_render=list(tweetes_to_render.filter(created_at__gte=start_time).order_by('-created_at')[0:500]);
    elif start_time == '' and end_time != '':
        tweetes_to_render=list(tweetes_to_render.filter(created_at__lte=end_time).order_by('-created_at')[0:500]);
    elif start_time != '' and end_time != '':
        tweetes_to_render=list(tweetes_to_render.filter(created_at__range=[start_time, end_time]).order_by('-created_at')[0:500]);

    tweets_dict = {}
    tweets_dict[''] = ''
    i = 1
    x = 0
    print(len(tweetes_to_render))
    print('Handling duplicates')
    #content_return['statuses'] = []
    content_return['statuses'] = [[] for m in range(min(150, len(tweetes_to_render)))]
    while x < min(150, len(tweetes_to_render)):
        tweet_render = tweetes_to_render[x];

        if tweet_render.twitter_id in tweets_dict.keys():
            tweetes_to_render.pop(x);
        else:
            tweets_dict[tweet_render.twitter_id] = tweet_render.twitter_id
            content_return['statuses'][x] = model_to_dict(tweetes_to_render[x]);
            content_return['statuses'][x]['created_at']=tweetes_to_render[x].created_at.strftime('%a %b %d %X %z %Y');
            content_return['statuses'][x]['r_correction_time']='';
            content_return['statuses'][x]['s_correction_time']='';
            content_return['statuses'][x]['q_correction_time']='';
            content_return['statuses'][x]['p_correction_time']='';
            content_return['statuses'][x]['user_followers_count']=tweetes_to_render[x].tweeter.tweeter_followers_count;
            content_return['statuses'][x]['user_profile_image_url']=tweetes_to_render[x].tweeter.tweeter_profile_image_url;
            content_return['statuses'][x]['user_location']=tweetes_to_render[x].tweeter.tweeter_location;
            content_return['statuses'][x]['tweeter_name']=tweetes_to_render[x].tweeter.tweeter_name;
            content_return['statuses'][x]['tweeter_sname']=tweetes_to_render[x].tweeter.tweeter_sname;
            content_return['statuses'][x]['price_time_then']=tweetes_to_render[x].stocksprices.time.strftime('%a %b %d %I:%M %p');
            price_list = StocksPrices.objects.filter(id__gte=tweetes_to_render[x].stocksprices.id).filter(stock_id=tweetes_to_render[x].stock_id).values('close')
            content_return['statuses'][x]['price_then']=str(tweetes_to_render[x].stocksprices.close) + ' (Range H: ' + str(price_list.aggregate(Max('close'))['close__max']) + ' - L: ' + str(price_list.aggregate(Min('close'))['close__min']) + ' Latest: ' + str(price_list[len(price_list)-1]['close']) + ')'
            duplicate_tweets = Opinion.objects.filter(twitter_id=tweet_render.twitter_id).select_related('stocksprices')
            l = len(duplicate_tweets)
            content_return['statuses'][x]['r_correction_time'] = [{} for m in range(l)]
            for m in range(0,l):
                dd = duplicate_tweets[m]
                content_return['statuses'][x]['r_correction_time'][m]['id'] = dd.id
                content_return['statuses'][x]['r_correction_time'][m]['stock_id'] = dd.stock_id
                content_return['statuses'][x]['r_correction_time'][m]['stock'] = dd.stock.stock
                price_list = StocksPrices.objects.filter(id__gte=dd.stocksprices.id).filter(stock_id=dd.stock_id).values('close')
                content_return['statuses'][x]['r_correction_time'][m]['price'] = str(dd.stocksprices.close) + ' (Range H: ' + str(price_list.aggregate(Max('close'))['close__max']) + ' - L: ' + str(price_list.aggregate(Min('close'))['close__min']) + ' Latest: ' + str(price_list[len(price_list)-1]['close']) + ')'

            x=x+1
            
    return content_return 

@ajax
def get_tweets(request):
    stock_name = request.POST['query']
    start_time = request.POST['start']
    end_time = request.POST['end']
    content_return = {}
    print(start_time)
    stock_id = Stocks.objects.filter(stock=stock_name)[0].stock_id

    try:
        price_list = StocksPrices.objects.filter(stock=stock_id).order_by('-id')
        price = price_list[0].close
        print('Price in DB')
    except:
        price = 0

    from django.utils import timezone 
    content_return['price'] = price
    print("get tweets")

    if start_time == '' and end_time == '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id).filter(labeled = False).filter(head_opinion= True).filter(stocksprices_id__isnull=False).filter(source_id=1).filter(similarId__isnull=True).exclude(labeled_user=request.user.username).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);
    elif start_time != '' and end_time == '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id).filter(labeled = False).filter(head_opinion= True).filter(created_at__gte=start_time).filter(source_id=1).filter(stocksprices_id__isnull=False).filter(similarId__isnull=True).exclude(labeled_user=request.user.username).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);
    elif start_time == '' and end_time != '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id).filter(labeled = False).filter(source_id=1).filter(head_opinion= True).filter(created_at__lte=end_time).filter(stocksprices_id__isnull=False).filter(similarId__isnull=True).exclude(labeled_user=request.user.username).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);
    elif start_time != '' and end_time != '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id).filter(labeled = False).filter(source_id=1).filter(head_opinion= True).filter(created_at__range=[start_time, end_time]).filter(stocksprices_id__isnull=False).filter(similarId__isnull=True).exclude(labeled_user=request.user.username).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);

    #prevent Duplicate 
    tweets_dict = {}
    tweets_dict[''] = ''
    i = 1
    x = 0
    print(len(tweetes_to_render))
    print('Handling duplicates')
    content_return['statuses'] = [[] for m in range(min(150, len(tweetes_to_render)))]
    content_return['stock'] = Stocks.objects.values_list('full_name_arabic', flat=True).filter(stock_id=stock_id);
    #content_return['statuses'] = []
    while x < min(150, len(tweetes_to_render)):
        tweet_render=tweetes_to_render[x];
        tweet_render_text=tweet_render.text.strip()
        tweet_render_text=re.sub(r"RT @\w*\w: ", '', tweet_render_text, flags=re.MULTILINE)
        tweet_render_text=re.sub(r'\.\.\.', '', tweet_render_text, flags=re.MULTILINE)
        try:
            urls=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet_render_text);
            for i in range(0,len(urls)):
                rep='r\''+urls[i]+'\''
                tweet_render_text=re.sub(r""+urls[i]+"", '', tweet_render_text, flags=re.MULTILINE)
        except:
            pass
        
        #print(x) 
        if tweet_render_text in tweets_dict.keys():
            #tweet = Opinion.objects.filter(twitter_id=tweet_render.get('twitter_id'))[0]
            #tweet.similarId = tweets_dict[tweet_render_text]
            #tweet.save();
            tweetes_to_render.pop(x); 
            #if (len(tweetes_to_render) > 150+i):
            #    tweetes_to_render.append(tweetes_to_render[149+i])
            #    i=i+1
        elif(tweet_render.labeled_user == request.user.username or tweet_render.labeled_user_second == request.user.username) and request.user.username != '':
            tweetes_to_render.remove(tweet_render)
            #if (len(tweetes_to_render) > 150+i):
            #    tweetes_to_render.append(tweetes_to_render[149+i])
            #    i=i+1
        else:
            #content_return['statuses'].append(model_to_dict(tweetes_to_render[x]))
            content_return['statuses'][x] = model_to_dict(tweetes_to_render[x]);
            content_return['statuses'][x]['created_at']=tweetes_to_render[x].created_at.strftime('%a %b %d %X %z %Y');
            content_return['statuses'][x]['r_correction_time']='';
            content_return['statuses'][x]['s_correction_time']='';
            content_return['statuses'][x]['q_correction_time']='';
            content_return['statuses'][x]['p_correction_time']='';
            content_return['statuses'][x]['user_followers_count']=tweetes_to_render[x].tweeter.tweeter_followers_count;
            content_return['statuses'][x]['user_profile_image_url']=tweetes_to_render[x].tweeter.tweeter_profile_image_url;
            content_return['statuses'][x]['user_location']=tweetes_to_render[x].tweeter.tweeter_location;
            content_return['statuses'][x]['tweeter_name']=tweetes_to_render[x].tweeter.tweeter_name;
            content_return['statuses'][x]['tweeter_sname']=tweetes_to_render[x].tweeter.tweeter_sname;
            content_return['statuses'][x]['price_time_then']=tweetes_to_render[x].stocksprices.time.strftime('%a %b %d %I:%M %p');
            content_return['statuses'][x]['price_then']=tweetes_to_render[x].stocksprices.close
            try:
                if tweetes_to_render[x].conversation_reply != '' and tweetes_to_render[x].conversation_reply != None:
                    #print(tweetes_to_render[x]['conversation_reply'])
                    tweet = Opinion.objects.filter(stock=stock_id,twitter_id=tweetes_to_render[x].conversation_reply).select_related('stocksprices').select_related('tweeter')[0]
                    content_return['statuses'].append([]);    
                    tweetes_to_render.insert(x+1,tweet);    
                x=x+1
            except:
                pass
            tweets_dict[tweet_render_text] = tweet_render.twitter_id
            
    #content_return['statuses'] = tweetes_to_render[0:150]

    print(len(tweetes_to_render)) 
    print('Start stats')
    # Fill in total number of entries in DB for this stock
    # Full DB
    content_return['total_entries_in_DB'] = StockCounter.objects.aggregate(Sum('counter'))['counter__sum']
    if(LabledCounter.objects.aggregate(Sum('counter'))['counter__sum'] != None):
        content_return['total_labeled_entries_in_DB'] = LabledCounter.objects.aggregate(Sum('counter'))['counter__sum']
    else:
        content_return['total_labeled_entries_in_DB'] = 0
    content_return['total_relevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`relevancy` = 'relevant' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_irrelevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`relevancy` = 'irrelevant' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_positive_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_negative_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_neutral_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']

    # Stock DB
    try:
        content_return['stock_entries_in_DB'] = StockCounter.objects.extra(where={"`stock` = '"+stock_name+"' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_entries_in_DB'] = 0
    try:
        content_return['stock_labeled_entries_in_DB'] = LabledCounter.objects.extra(where={"`stock` = '"+stock_name+"' "}).values()[0]['counter']
    except:
        content_return['stock_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_relevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `relevancy` = 'relevant' "}).values()[0]['counter']
    except:
        content_return['stock_relevant_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_irrelevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `relevancy` = 'irrelevant' "}).values()[0]['counter']
    except:
        content_return['stock_irrelevant_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_positive_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_positive_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_negative_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_negative_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_neutral_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_neutral_labeled_entries_in_DB'] = 0

    #user counters
    try:
        content_return['user_relevant_for_stock_in_DB'] = UserCounter.objects.filter(labeled_user=request.user.username,stock=stock_name,relevancy='relevant').aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['user_relevant_for_stock_in_DB'] = 0
    try:
        content_return['user_irrelevant_for_stock_in_DB'] = UserCounter.objects.filter(labeled_user=request.user.username,stock=stock_name,relevancy='irrelevant').aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['user_irrelevant_for_stock_in_DB'] = 0
    content_return['user_total_labels_in_DB'] = UserCounter.objects.filter(labeled_user=request.user.username).aggregate(Sum('counter'))['counter__sum']

    print('Done get tweets')
    #gc.collect()
    return content_return 

#@login_required
@ajax
def get_tweets_proto(request):
    stock_name = request.POST['query']

    content_return = {}
    #query = stock_name
    #query = synonyms[query]

    #remove the adult content
    #naughty_words=" AND ( -ﺰﺑ -ﻂﻳﺯ -ﻂﻴﻇ -ﺲﻜﺳ -ﺲﻜﺴﻳ -ﺲﺣﺎﻗ -ﺞﻨﺳ -ﻦﻴﻛ -ﺞﻨﺳ -ﺏﺯ -ﺏﺯﺍﺯ -ﻚﺳ -ﻒﺤﻟ -ﻒﺣﻮﻠﻫ -ﺬﺑ )"
    stock_id = Stocks.objects.filter(stock=stock_name)[0].stock_id
    
    '''
    #tweets = twitter.search(q= query + 'OR ' + synonyms[query], result_type='recent')
    try:
        tweets = twitter.search(q=query, result_type='recent')
    except:
        from twython import Twython
        twitter = Twython("MGMeNEK5bEqADjJRDJmQ8Yy1f", "eVR1kjrTdHPEiFuLoAEA6pPGSnuZ1NnAa1EwtqBi4wVA1tbRHo", "91079548-uhlRrwtgVQcavlf3lv4Dy1ZFCq5CXvBQFvc5A1l0n", "V6vLsqzqrdfs2YX4I1NVG2gP845gjTrBSDNxHVz496g66")
        tweets = twitter.search(q=query, result_type='recent')
    '''
    
    try:
        tweets = twitterCrawler.SearchQueryAPI(query, -1, -1)
    except:        
        PROJECT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
        configFileCrawler = os.path.join(PROJECT_DIR, 'TwitterCrawler','Configurations', 'Configurations_Proto.xml')
        twitterCrawler = TwitterCrawler(configFileCrawler, None, None, None)
        #tweets = twitterCrawler.SearchQueryAPI(query, -1, -1)

    try:
        price_list = StocksPrices.objects.filter(stock=stock_id).order_by('-id')
        price = price_list[0].close
        print('Price in DB')
    except:
        price = 0


    from django.utils import timezone 
    content_return['price'] = price
    #tweets['price'] = CorrectionData.objects.get(stock_name=query)
    '''
    print('Saving tweets')
        
    for tweet in tweets:
        tweet_exist = Opinion.objects.filter(twitter_id=tweet['id_str'])
        if(len(tweet_exist) == 0):
            try:
                item = Opinion()
                item.twitter_id = tweet['id_str']
                item.user_id = tweet['user']['id']
                item.text = tweet['text']
                item.created_at = tweet['created_at']
                item.user_followers_count = tweet['user']['followers_count']
                item.user_profile_image_url = tweet['user']['profile_image_url']
                item.media_url = tweet['entities']
                item.tweeter_sname = tweet['user']['screen_name']
                item.tweeter_name = tweet['user']['name']
                #print('kkkkkkk'+str(tweet['entities']))
                item.pub_date = str(timezone.now())
                item.stock = stock_name
                item.labeled = False
                item.source = "twitter.com"
                if ' ﺰﺑ ' in tweet['text'] and ' ﻂﻳﺯ ' in tweet['text'] and ' ﻂﻴﻇ ' in tweet['text'] and ' ﺲﻜﺳ ' in tweet['text'] and ' ﺲﻜﺴﻳ ' in tweet['text'] and ' ﺲﺣﺎﻗ ' in tweet['text'] and ' ﺞﻨﺳ ' in tweet['text'] and ' ﺏﺯ ' in tweet['text'] and ' ﺏﺯﺍﺯ ' in tweet['text'] and ' ﻂﻳﺯ ' in tweet['text'] and ' ﻂﻳﺯ ' in tweet['text'] and ' ﻂﻳﺯ ' in tweet['text'] and ' ﻚﺳ ' in tweet['text'] and ' ﻒﺤﻟ ' in tweet['text'] and ' ﻒﺣﻮﻠﻫ ' in tweet['text'] and ' ﺬﺑ ' in tweet['text']:
                    print(tweet['text'])
                else:
                    item.save()
            except Exception as e: 
              pass
    print('Tweets saved')
    '''
    tweetes_to_render=list(Opinion.objects.filter(stock=stock_id,created_at__isnull=False).exclude(similarId__isnull=True).values().order_by('-created_at')[0:50]);
    #tweetes_to_render_temp = Opinion.objects.filter(stock=stock_name).values().order_by('-id')[:20]
    #tweetes_to_render = sorted(tweetes_to_render_temp, key=lambda x: time.strptime(x['created_at'],'%a %b %d %X %z %Y'), reverse=True)[0:50];

    #tweetes_to_render = sorted(tweetes_to_render_temp, key=lambda x: time.strptime(x['created_at'],'%a %b %d %X %z %Y'), reverse=True);
    #my_list = list(tweetes_to_render)
    #print(json.dumps(my_list[0]))
    #tweetes_to_render_temp = Opview.objects.filter(stock=stock_name, labeled = False).values();
    #tweetes_to_render = sorted(tweetes_to_render_temp, key=lambda x: time.strptime(x['created_at'],'%a %b %d %X %z %Y'), reverse=True);

    #prevent Duplicate 
    tweets_dict = {}
    tweets_dict[''] = ''
    i = 1
    x = 0
    print('Handling duplicates')
    while x < min(50, len(tweetes_to_render)):
        try:
            tweet_render=tweetes_to_render[x];
                                
            # Get the tweet by ID 
            #retrievedTweet = dict(twitterCrawler.GetSingleTweetByID(tweet_render.get('twitter_id')))

            
            # Update the text in the tweet data
            #tweet_text = retrievedTweet['text']
            tweet_text = tweet_render['text']
            tweet_render['text'] = tweet_text
            if tweet_text.strip() in tweets_dict.keys():
                tweet = Opinion.objects.filter(twitter_id=tweet_render.get('twitter_id'))[0]
                #tweet.similarId = tweets_dict[tweet_render['text']]
                #tweet.save()
                tweetes_to_render.pop(x); 
                if (len(tweetes_to_render_temp) > 50+i):
                    tweetes_to_render.append(tweetes_to_render_temp[49+i])
                    i=i+1
            elif(request.user.username != "" and (tweet_render.get('labeled_user') == request.user.username or tweet_render.get('labeled_user_second') == request.user.username)):
                tweetes_to_render.remove(tweet_render)
                if (len(tweetes_to_render_temp) > 50+i):
                    tweetes_to_render.append(tweetes_to_render_temp[49+i])
                    i=i+1
            else:
                x=x+1
                tweets_dict[tweet_render.get('text').strip()] = tweet_render.get('twitter_id')

        except Exception as e:
            # Rate limit exceeded
            print('Error: ' + str(e)) 
            if('Twitter sent status 429' in str(e)):
                # Sleep 15 min, only 180 calls permitted per 15 min
                time.sleep(900)
                x=x+1
            elif('Twitter sent status 404' in str(e)):
                # Update the text in the tweet data
                tweet_text = 'Sorry, this tweet is not available for the free service'
                tweet_render['text'] = tweet_text
                if tweet_text.strip() in tweets_dict.keys():
                    tweet = Opinion.objects.filter(twitter_id=tweet_render.get('twitter_id'))[0]
                    #tweet.similarId = tweets_dict[tweet_render['text']]
                    #tweet.save()
                    tweetes_to_render.pop(x); 
                    if (len(tweetes_to_render_temp) > 50+i):
                        tweetes_to_render.append(tweetes_to_render_temp[49+i])
                        i=i+1
                elif(request.user.username != "" and (tweet_render.get('labeled_user') == request.user.username or tweet_render.get('labeled_user_second') == request.user.username)):
                    tweetes_to_render.remove(tweet_render)
                    if (len(tweetes_to_render_temp) > 50+i):
                        tweetes_to_render.append(tweetes_to_render_temp[49+i])
                        i=i+1
                else:
                    x=x+1
                    tweets_dict[tweet_render.get('text').strip()] = tweet_render.get('twitter_id')
            else:
                x=x+1
    content_return['statuses'] = tweetes_to_render
    
    print('Start stats')
    # Fill in total number of entries in DB for this stock
    # Full DB
    content_return['total_entries_in_DB'] = StockCounter.objects.aggregate(Sum('counter'))['counter__sum']
    if(LabledCounter.objects.aggregate(Sum('counter'))['counter__sum'] != None):
        content_return['total_labeled_entries_in_DB'] = LabledCounter.objects.aggregate(Sum('counter'))['counter__sum']
    else    :
        content_return['total_labeled_entries_in_DB'] = 0
    content_return['total_relevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`relevancy` = 'relevant' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_irrelevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`relevancy` = 'irrelevant' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_positive_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_negative_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_neutral_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']

    # Stock DB
    try:
        content_return['stock_entries_in_DB'] = StockCounter.objects.extra(where={"`stock` = '"+stock_name+"' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_entries_in_DB'] = 0
    try:
        content_return['stock_labeled_entries_in_DB'] = LabledCounter.objects.extra(where={"`stock` = '"+stock_name+"' "}).values()[0]['counter']
    except:
        content_return['stock_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_relevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `relevancy` = 'relevant' "}).values()[0]['counter']
    except:
        content_return['stock_relevant_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_irrelevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `relevancy` = 'irrelevant' "}).values()[0]['counter']
    except:
        content_return['stock_irrelevant_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_positive_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_positive_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_negative_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_negative_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_neutral_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_neutral_labeled_entries_in_DB'] = 0
    print('Done')
    return content_return 

@ajax
def get_tweets_filtered(request):
    #gc.collect()
    stock_name = request.POST['query']
    start_time = request.POST['start']
    end_time = request.POST['end']
    stock_name = request.POST['query']
    content_return = {}
    stock_id = Stocks.objects.filter(stock=stock_name)[0].stock_id

    try:
        price_list = StocksPrices.objects.filter(stock=stock_id).order_by('-id')
        price = price_list[0].close
        print('Price in DB')
    except:
        price = 0

    from django.utils import timezone 
    content_return['price'] = price

    if start_time == '' and end_time == '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id, labeled = False, head_opinion= True, created_at__isnull=False,stocksprices_id__isnull=False).filter(similarId__isnull=True).filter(r_correction__isnull=True).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);
    elif start_time != '' and end_time == '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id, labeled = False, head_opinion= True,created_at__gte=start_time,created_at__isnull=False,stocksprices_id__isnull=False).filter(similarId__isnull=True).filter(r_correction__isnull=True).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);
    elif start_time == '' and end_time != '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id, labeled = False, head_opinion= True, created_at__lte=end_time,created_at__isnull=False,stocksprices_id__isnull=False).filter(similarId__isnull=True).filter(r_correction__isnull=True).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);
    elif start_time != '' and end_time != '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id, labeled = False, head_opinion= True,created_at__range=[start_time, end_time],created_at__isnull=False,stocksprices_id__isnull=False).filter(similarId__isnull=True).filter(r_correction__isnull=True).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);

    #prevent Duplicate 
    tweets_dict = {}
    tweets_dict[''] = ''
    i = 1
    x = 0
    print(len(tweetes_to_render))
    print('Filtered Handling duplicates')
    content_return['statuses'] = [[] for m in range(min(150, len(tweetes_to_render)))]
    content_return['stock'] = Stocks.objects.values_list('full_name_arabic', flat=True).filter(stock_id=stock_id);
    #content_return['statuses'] = []
    print('before while' + str(x))
    while x < min(150, len(tweetes_to_render)):
        tweet_render=tweetes_to_render[x];
        tweet_render_text=tweet_render.text.strip()
        tweet_render_text=re.sub(r"RT @\w*\w: ", '', tweet_render_text, flags=re.MULTILINE)
        tweet_render_text=re.sub(r'\.\.\.', '', tweet_render_text, flags=re.MULTILINE)
        try:
            urls=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet_render_text);
            for i in range(0,len(urls)):
                rep='r\''+urls[i]+'\''
                tweet_render_text=re.sub(r""+urls[i]+"", '', tweet_render_text, flags=re.MULTILINE)
        except:
            pass
        
        #print(x) 
        # Classify the tweet
        content_return['statuses'][x]['r_correction_time']='';
        content_return['statuses'][x]['s_correction_time']='';
        content_return['statuses'][x]['p_correction_time']='';
        content_return['statuses'][x]['q_correction_time']='';
        PROJECT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
        filter = Filter(PROJECT_DIR, 'tasnee3', False)
        print(x)
        print('filter: ' +str(filter))
        text = [] 
        text.append(tweet_render_text)
        labels = filter.Classify(text)
        print('labels: ' + str(labels))
        label = labels[0]
        if label == 1: # If irrelevant remove it
            tweetes_to_render.remove(tweet_render)
        elif tweet_render_text in tweets_dict.keys():
            #tweet = Opinion.objects.filter(twitter_id=tweet_render.get('twitter_id'))[0]
            #tweet.similarId = tweets_dict[tweet_render_text]
            #tweet.save();
            tweetes_to_render.pop(x); 
            #if (len(tweetes_to_render) > 150+i):
            #    tweetes_to_render.append(tweetes_to_render[149+i])
            #    i=i+1
        elif(tweet_render.labeled_user == request.user.username or tweet_render.labeled_user_second == request.user.username) and request.user.username != '':
            tweetes_to_render.remove(tweet_render)
            #if (len(tweetes_to_render) > 150+i):
            #    tweetes_to_render.append(tweetes_to_render[149+i])
            #    i=i+1
        else:
            #content_return['statuses'].append(model_to_dict(tweetes_to_render[x]))
            content_return['statuses'][x] = model_to_dict(tweetes_to_render[x]);
            content_return['statuses'][x]['created_at']=tweetes_to_render[x].created_at.strftime('%a %b %d %X %z %Y');
            content_return['statuses'][x]['r_correction_time']='';
            content_return['statuses'][x]['s_correction_time']='';
            content_return['statuses'][x]['q_correction_time']='';
            content_return['statuses'][x]['p_correction_time']='';
            content_return['statuses'][x]['user_followers_count']=tweetes_to_render[x].tweeter.tweeter_followers_count;
            content_return['statuses'][x]['user_profile_image_url']=tweetes_to_render[x].tweeter.tweeter_profile_image_url;
            content_return['statuses'][x]['user_location']=tweetes_to_render[x].tweeter.tweeter_location;
            content_return['statuses'][x]['tweeter_name']=tweetes_to_render[x].tweeter.tweeter_name;
            content_return['statuses'][x]['tweeter_sname']=tweetes_to_render[x].tweeter.tweeter_sname;
            content_return['statuses'][x]['price_time_then']=tweetes_to_render[x].stocksprices.time.strftime('%a %b %d %I:%M %p');
            content_return['statuses'][x]['price_then']=tweetes_to_render[x].stocksprices.close
            try:
                if tweetes_to_render[x].conversation_reply != '' and tweetes_to_render[x].conversation_reply != None:
                    #print(tweetes_to_render[x]['conversation_reply'])
                    tweet = Opinion.objects.filter(stock=stock_id,twitter_id=tweetes_to_render[x].conversation_reply).select_related('stocksprices').select_related('tweeter')[0]
                    content_return['statuses'].append([]);    
                    tweetes_to_render.insert(x+1,tweet);    
                x=x+1
            except:
                pass
            tweets_dict[tweet_render_text] = tweet_render.twitter_id
        print(tweetes_to_render[x].r_correction)
            
    #content_return['statuses'] = tweetes_to_render[0:150]

    print(len(tweetes_to_render)) 
    print('Start stats')
    # Fill in total number of entries in DB for this stock
    # Full DB
    content_return['total_entries_in_DB'] = StockCounter.objects.aggregate(Sum('counter'))['counter__sum']
    if(LabledCounter.objects.aggregate(Sum('counter'))['counter__sum'] != None):
        content_return['total_labeled_entries_in_DB'] = LabledCounter.objects.aggregate(Sum('counter'))['counter__sum']
    else:
        content_return['total_labeled_entries_in_DB'] = 0
    content_return['total_relevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`relevancy` = 'relevant' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_irrelevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`relevancy` = 'irrelevant' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_positive_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_negative_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_neutral_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']

    # Stock DB
    try:
        content_return['stock_entries_in_DB'] = StockCounter.objects.extra(where={"`stock` = '"+stock_name+"' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_entries_in_DB'] = 0
    try:
        content_return['stock_labeled_entries_in_DB'] = LabledCounter.objects.extra(where={"`stock` = '"+stock_name+"' "}).values()[0]['counter']
    except:
        content_return['stock_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_relevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `relevancy` = 'relevant' "}).values()[0]['counter']
    except:
        content_return['stock_relevant_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_irrelevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `relevancy` = 'irrelevant' "}).values()[0]['counter']
    except:
        content_return['stock_irrelevant_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_positive_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_positive_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_negative_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_negative_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_neutral_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_neutral_labeled_entries_in_DB'] = 0

    #user counters
    try:
        content_return['user_relevant_for_stock_in_DB'] = UserCounter.objects.filter(labeled_user=request.user.username,stock=stock_name,relevancy='relevant').aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['user_relevant_for_stock_in_DB'] = 0
    try:
        content_return['user_irrelevant_for_stock_in_DB'] = UserCounter.objects.filter(labeled_user=request.user.username,stock=stock_name,relevancy='irrelevant').aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['user_irrelevant_for_stock_in_DB'] = 0
    content_return['user_total_labels_in_DB'] = UserCounter.objects.filter(labeled_user=request.user.username).aggregate(Sum('counter'))['counter__sum']
    print('Done')
    #gc.collect()
    return content_return 

@ajax
def add_tweet_by_ref(request):
    stock_name = request.POST['stock_name']
    ref_tweet_id = request.POST['ref_tweet']
    stock_id = Stocks.objects.filter(stock=stock_name)[0].stock_id
    ref_tweet = Opinion.objects.filter(id=ref_tweet_id)[0]
    id_list = Opinion.objects.filter(created_at__gte=ref_tweet.created_at).values_list('id', flat=True).order_by('id')[0:20]
    item = copy.copy(ref_tweet)
    counter = 1;
    contin = True;
    while (counter < 20 and contin):
        if(id_list[0]+counter not in id_list):
            item.id=id_list[0]+counter
            contin = False;
        counter = counter + 1;

    time = ref_tweet.created_at+timedelta(hours=3)
    price = StocksPrices.objects.filter(stock=stock_id).filter(time__lte=time).order_by('-id')[0]
   
    item.stocksprices_id = price.id
    item.stock_id = stock_id
    item.relevancy = None
    item.sentiment = None
    item.question = None
    item.pricetarget = None
    item.p_relevancy = None
    item.p_sentiment = None
    item.p_question = None
    item.p_pricetarget = None
    item.r_correction = None
    item.s_correction = None
    item.q_correction = None
    item.p_correction = None
    item.r_correction_time = None
    item.s_correction_time = None
    item.q_correction_time = None
    item.p_correction_time = None
    item.labeled_user_third = "added from training page"
    item.save()
    return { 'id': item.id, 'stock_id': stock_id , 'price': price.close }

@ajax
def get_tweets_predicted(request):
    stock_name = request.POST['query']
    start_time = request.POST['start']
    end_time = request.POST['end']
    content_return = {}
    print(start_time)
    stock_id = Stocks.objects.filter(stock=stock_name)[0].stock_id

    try:
        price_list = StocksPrices.objects.filter(stock=stock_id).order_by('-id')
        price = price_list[0].close
        print('Price in DB')
    except:
        price = 0

    from django.utils import timezone 
    content_return['price'] = price
    print("get tweets")

    if start_time == '' and end_time == '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id, labeled = False, created_at__isnull=False,stocksprices_id__isnull=False).filter(source_id=1).filter(similarId__isnull=True).filter(head_opinion= True).filter(relevancy='').filter(r_correction__isnull=True).filter(p_relevancy__isnull=False).filter(p_sentiment__isnull=False).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);
    elif start_time != '' and end_time == '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id, labeled = False, created_at__gte=start_time,created_at__isnull=False,stocksprices_id__isnull=False).filter(source_id=1).filter(head_opinion= True).filter(similarId__isnull=True).filter(relevancy='').filter(r_correction__isnull=True).filter(p_relevancy__isnull=False).filter(p_sentiment__isnull=False).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);
    elif start_time == '' and end_time != '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id, labeled = False, created_at__lte=end_time,created_at__isnull=False,stocksprices_id__isnull=False).filter(source_id=1).filter(head_opinion= True).filter(similarId__isnull=True).filter(relevancy='').filter(r_correction__isnull=True).filter(p_relevancy__isnull=False).filter(p_sentiment__isnull=False).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);
    elif start_time != '' and end_time != '':
        tweetes_to_render=list(Opinion.objects.filter(stock=stock_id, labeled = False, created_at__range=[start_time, end_time],created_at__isnull=False,stocksprices_id__isnull=False).filter(source_id=1).filter(similarId__isnull=True).filter(head_opinion= True).filter(relevancy='').filter(p_relevancy__isnull=False).filter(p_sentiment__isnull=False).filter(r_correction__isnull=True).select_related('tweeter').select_related('stocksprices').order_by('-created_at')[0:500]);

    #prevent Duplicate 
    tweets_dict = {}
    tweets_dict[''] = ''
    i = 1
    x = 0
    print(len(tweetes_to_render))
    print('Handling duplicates')
    content_return['statuses'] = [[] for m in range(min(150, len(tweetes_to_render)))]
    content_return['stock'] = Stocks.objects.values_list('full_name_arabic', flat=True).filter(stock_id=stock_id);
    #content_return['statuses'] = []
    while x < min(150, len(tweetes_to_render)):
        tweet_render=tweetes_to_render[x];
        tweet_render_text=tweet_render.text.strip()
        tweet_render_text=re.sub(r"RT @\w*\w: ", '', tweet_render_text, flags=re.MULTILINE)
        tweet_render_text=re.sub(r'\.\.\.', '', tweet_render_text, flags=re.MULTILINE)
        try:
            urls=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet_render_text);
            for i in range(0,len(urls)):
                rep='r\''+urls[i]+'\''
                tweet_render_text=re.sub(r""+urls[i]+"", '', tweet_render_text, flags=re.MULTILINE)
        except:
            pass
        
        #print(x) 
        if tweet_render_text in tweets_dict.keys():
            #tweet = Opinion.objects.filter(twitter_id=tweet_render.get('twitter_id'))[0]
            #tweet.similarId = tweets_dict[tweet_render_text]
            #tweet.save();
            tweetes_to_render.pop(x); 
            #if (len(tweetes_to_render) > 150+i):
            #    tweetes_to_render.append(tweetes_to_render[149+i])
            #    i=i+1
        elif(tweet_render.labeled_user == request.user.username or tweet_render.labeled_user_second == request.user.username) and request.user.username != '':
            tweetes_to_render.remove(tweet_render)
            #if (len(tweetes_to_render) > 150+i):
            #    tweetes_to_render.append(tweetes_to_render[149+i])
            #    i=i+1
        else:
            #content_return['statuses'].append(model_to_dict(tweetes_to_render[x]))
            content_return['statuses'][x] = model_to_dict(tweetes_to_render[x]);
            content_return['statuses'][x]['created_at']=tweetes_to_render[x].created_at.strftime('%a %b %d %X %z %Y');
            content_return['statuses'][x]['r_correction_time']='';
            content_return['statuses'][x]['s_correction_time']='';
            content_return['statuses'][x]['q_correction_time']='';
            content_return['statuses'][x]['p_correction_time']='';
            content_return['statuses'][x]['user_followers_count']=tweetes_to_render[x].tweeter.tweeter_followers_count;
            content_return['statuses'][x]['user_profile_image_url']=tweetes_to_render[x].tweeter.tweeter_profile_image_url;
            content_return['statuses'][x]['user_location']=tweetes_to_render[x].tweeter.tweeter_location;
            content_return['statuses'][x]['tweeter_name']=tweetes_to_render[x].tweeter.tweeter_name;
            content_return['statuses'][x]['tweeter_sname']=tweetes_to_render[x].tweeter.tweeter_sname;
            content_return['statuses'][x]['price_time_then']=tweetes_to_render[x].stocksprices.time.strftime('%a %b %d %I:%M %p');
            content_return['statuses'][x]['price_then']=tweetes_to_render[x].stocksprices.close
            content_return['statuses'][x]['p_relevancy']=tweetes_to_render[x].p_relevancy

            if( tweetes_to_render[x].p_question == 1 ):
                content_return['statuses'][x]['p_question'] = "question";
            elif( tweetes_to_render[x].p_question == 0 ):
                content_return['statuses'][x]['p_question'] = "Not a question";
            else:
                content_return['statuses'][x]['p_question'] = "none"

            if( tweetes_to_render[x].p_pricetarget == 1 ):
                content_return['statuses'][x]['p_pricetarget'] = "Pricetarget";
            elif( tweetes_to_render[x].p_pricetarget == 0 ):
                content_return['statuses'][x]['p_pricetarget'] = "Not a pricetarget";
            else:
                content_return['statuses'][x]['p_pricetarget'] = "none"

            xx=x
            try:
                if tweetes_to_render[x].conversation_reply != '' and tweetes_to_render[x].conversation_reply != None:
                    #print(tweetes_to_render[x]['conversation_reply'])
                    tweet = Opinion.objects.filter(stock=stock_id,twitter_id=tweetes_to_render[x].conversation_reply).select_related('stocksprices').select_related('tweeter')[0]
                    content_return['statuses'].append([]);    
                    tweetes_to_render.insert(x+1,tweet);    
                x=x+1
            except:
                pass

            duplicate_tweets = Opinion.objects.filter(twitter_id=tweet_render.twitter_id).exclude(stock_id=stock_id).select_related('stocksprices').select_related('tweeter')
            l = len(duplicate_tweets)
            first_question = content_return['statuses'][xx]['p_question'] or "Not a question"
            content_return['statuses'][xx]['r_correction_time'] = [{} for m in range(l+1)]
            #print(content_return['statuses'][xx]['r_correction_time'])
            content_return['statuses'][xx]['r_correction_time'][0] = { 'id': content_return['statuses'][xx]['id'], 'stock_id': content_return['statuses'][xx]['stock'], 'stock': tweetes_to_render[xx].stock.stock, 'p_relevancy': content_return['statuses'][xx]['p_relevancy'], 'p_sentiment': content_return['statuses'][xx]['p_sentiment'], 'p_question': first_question , 'p_pricetarget': "Not a pricetarget", 'price': content_return['statuses'][xx]['price_then'], 'with_frame': False };
            ## re use of this parameter to send the list of duplicate tweets without adding more keys to the dictionary content_return
            for m in range(1,l+1):
                dd = duplicate_tweets[m-1]
    
                if( dd.p_question == 1 ):
                    adjusted_question = "question";
                elif( dd.p_question == 0 ):
                    adjusted_question = "Not a question";
                else:
                    adjusted_question = "none"
    
                if( dd.p_pricetarget == 1 ):
                    adjusted_pricetarget = "Pricetarget";
                elif( dd.p_pricetarget == 0 ):
                    adjusted_pricetarget = "Not a pricetarget";
                else:
                    adjusted_pricetarget = "none"
                
                content_return['statuses'][xx]['r_correction_time'][m]['with_frame'] = all(v is not None for v in [dd.r_correction, dd.s_correction, dd.q_correction, dd.p_correction]) 
                content_return['statuses'][xx]['r_correction_time'][m]['id'] = dd.id 
                content_return['statuses'][xx]['r_correction_time'][m]['stock_id'] = dd.stock_id 
                content_return['statuses'][xx]['r_correction_time'][m]['stock'] = dd.stock.stock
                content_return['statuses'][xx]['r_correction_time'][m]['p_relevancy'] = dd.p_relevancy
                content_return['statuses'][xx]['r_correction_time'][m]['p_sentiment'] = dd.p_sentiment
                content_return['statuses'][xx]['r_correction_time'][m]['p_question'] = adjusted_question
                content_return['statuses'][xx]['r_correction_time'][m]['p_pricetarget'] = adjusted_pricetarget
                content_return['statuses'][xx]['r_correction_time'][m]['price'] = dd.stocksprices.close

            tweets_dict[tweet_render_text] = tweet_render.twitter_id
            
    print(len(tweetes_to_render)) 
    print('Start stats')
    # Fill in total number of entries in DB for this stock
    # Full DB
    content_return['total_entries_in_DB'] = StockCounter.objects.aggregate(Sum('counter'))['counter__sum']
    if(LabledCounter.objects.aggregate(Sum('counter'))['counter__sum'] != None):
        content_return['total_labeled_entries_in_DB'] = LabledCounter.objects.aggregate(Sum('counter'))['counter__sum']
    else:
        content_return['total_labeled_entries_in_DB'] = 0
    content_return['total_relevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`relevancy` = 'relevant' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_irrelevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`relevancy` = 'irrelevant' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_positive_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_negative_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    content_return['total_neutral_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']

    # Stock DB
    try:
        content_return['stock_entries_in_DB'] = StockCounter.objects.extra(where={"`stock` = '"+stock_name+"' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_entries_in_DB'] = 0
    try:
        content_return['stock_labeled_entries_in_DB'] = LabledCounter.objects.extra(where={"`stock` = '"+stock_name+"' "}).values()[0]['counter']
    except:
        content_return['stock_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_relevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `relevancy` = 'relevant' "}).values()[0]['counter']
    except:
        content_return['stock_relevant_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_irrelevant_labeled_entries_in_DB'] = RelevancyCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `relevancy` = 'irrelevant' "}).values()[0]['counter']
    except:
        content_return['stock_irrelevant_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_positive_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'positive' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_positive_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_negative_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'negative' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_negative_labeled_entries_in_DB'] = 0
    try:
        content_return['stock_neutral_labeled_entries_in_DB'] = SentimentCounter.objects.extra(where={"`stock` = '"+stock_name+"' and `sentiment` = 'neutral' "}).aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['stock_neutral_labeled_entries_in_DB'] = 0

    #user counters
    try:
        content_return['user_relevant_for_stock_in_DB'] = UserCounter.objects.filter(labeled_user=request.user.username,stock=stock_name,relevancy='relevant').aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['user_relevant_for_stock_in_DB'] = 0
    try:
        content_return['user_irrelevant_for_stock_in_DB'] = UserCounter.objects.filter(labeled_user=request.user.username,stock=stock_name,relevancy='irrelevant').aggregate(Sum('counter'))['counter__sum']
    except:
        content_return['user_irrelevant_for_stock_in_DB'] = 0
    content_return['user_total_labels_in_DB'] = UserCounter.objects.filter(labeled_user=request.user.username).aggregate(Sum('counter'))['counter__sum']

    print('Done get tweets')
    #gc.collect()
    return content_return 


@ajax
def get_news(request):
    #gc.collect()
    stock_name = request.POST['query']
    s_id = Stocks.objects.filter(stock=stock_name)[0].stock_id
    content_return = []
    newsList=Opinion.objects.filter(stock_id=s_id).exclude(source_id=1).filter(labeled = False).filter(stocksprices_id__isnull=False).exclude(labeled_user=request.user.username).order_by('-id')[0:50];

    x=0
    while x < min(150, len(newsList)):
        newsItem=newsList[x]
        n=NewsItem()
        n.opinion_id = newsItem.id
        n.link = newsItem.media_url
        n.title = newsItem.text
        n.source_id = newsItem.source_id
        n.created_at = newsItem.created_at.strftime('%a %b %d %X %z %Y')
        n.price_time_then = newsItem.stocksprices.time.strftime('%a %b %d %I:%M %p');
        n.price_then = newsItem.stocksprices.close
        content_return.append({'media_url':n.link, 'title':n.title, 'source_id':n.source_id, 'created_at':n.created_at , 'price_time_then':n.price_time_then , 'price_then':n.price_then, 'opinion_id':n.opinion_id})
        x=x+1

    return content_return;


def getSimilarlabeling():
    duplicate_tweetes = Opinion.objects.exclude(similarId= None);
    for tweet in duplicate_tweetes:
        parent_tweet =  Opinion.objects.filter(twitter_id = tweet.similarId).values()[0]
        if parent_tweet['labeled'] == 1:
            tweet.voted_relevancy = parent_tweet['voted_relevancy']
            tweet.voted_sentiment = parent_tweet['voted_sentiment']
            tweet.labeled = True
            tweet.save()

@ajax
def correct(request):
    opinion_id = request.POST['opinion_id']
    stock_name = request.POST['stock']
    correction = int(request.POST['correction'])
    classifier = request.POST['classifier']
    s_id = Stocks.objects.filter(stock=stock_name)[0].stock_id

    print(opinion_id);
    tweet = Opinion.objects.filter(id=opinion_id)[0]
    if classifier == 'r' and tweet.p_relevancy != None:
        tweet.r_correction=correction
        tweet.r_correction_time=timezone.now()
        if correction == 1:
            tweet.relevancy = tweet.p_relevancy 
    elif classifier == 's' and tweet.p_sentiment != None:
        tweet.s_correction=correction
        tweet.s_correction_time=timezone.now()
        if correction == 1:
            tweet.sentiment = tweet.p_sentiment
    elif classifier == 'q' and tweet.p_question != None:
        tweet.q_correction=correction
        tweet.q_correction_time=timezone.now()
        if correction == 1:
            tweet.question = tweet.p_question
    elif classifier == 'p' and tweet.p_pricetarget != None:
        tweet.p_correction=correction
        tweet.p_correction_time=timezone.now()
        if correction == 1:
            tweet.pricetarget = tweet.p_pricetarget

    tweet.save()

@ajax
def get_correction(request):
    opinion_id = request.POST['opinion_id']
    stock_name = request.POST['stock']
    relevancy = request.POST['relevancy']
    sentiment = request.POST['sentiment']

    s_id = Stocks.objects.filter(stock=stock_name)[0].stock_id
    tweet = Opinion.objects.filter(id=opinion_id)[0]

    if(request.user.username == '' or request.user.username == None):
        print('ERROR: Empty user name')
        return
    
    if(request.POST['question'] == 'question'):
        tweet.question = 1
    elif(request.POST['question'] == 'notquestion'):
        tweet.question = 0

    if(request.POST['pricetarget'] == 'pricetarget'):
        tweet.pricetarget = 1
    elif(request.POST['pricetarget'] == 'notpricetarget'):
        tweet.pricetarget = 0
    
    #print(opinion_id) 
    #print(stock_name) 
    #print(s_id) 
    if(sentiment != 'none'):
        if(tweet.sentiment == 'none' or tweet.sentiment == '' or tweet.sentiment==None):
            tweet.sentiment = sentiment
            tweet.voted_sentiment = sentiment
        elif(tweet.sentiment_second == 'none' or tweet.sentiment_second == '' or tweet.sentiment_second == None):
            tweet.sentiment_second = sentiment
            if(tweet.sentiment == tweet.sentiment_second):
                tweet.sentiment_third= 'not_needed'
                tweet.voted_sentiment = sentiment
        elif(tweet.sentiment_third == 'none' or tweet.sentiment_third == '' or tweet.sentiment_third ==  None):
            tweet.sentiment_third = sentiment
            rel_list=[tweet.sentiment,tweet.sentiment_second,tweet.sentiment_third]
            tweet.voted_sentiment=max(((item, rel_list.count(item)) for item in set(rel_list)), key=lambda a: a[1])[0]

        #print('Sentiment')
    elif (relevancy != 'none'):
        if(tweet.relevancy == 'none' or tweet.relevancy == '' or tweet.relevancy == None):
            tweet.relevancy = relevancy
            tweet.labeled_user = request.user.username
        elif(tweet.relevancy_second == 'none' or tweet.relevancy_second == '' or tweet.relevancy_second == None):
            tweet.relevancy_second = relevancy
            tweet.labeled_user_second = request.user.username
            if(tweet.relevancy == tweet.relevancy_second):
                tweet.labeled_user_third='not_needed'
                tweet.relevancy_third='not_needed'
                tweet.voted_relevancy=tweet.relevancy
        elif(tweet.relevancy_third == 'none' or tweet.relevancy_third == '' or tweet.relevancy_third ==  None):
            tweet.relevancy_third = relevancy
            tweet.labeled_user_third = request.user.username
            rel_list=[tweet.relevancy,tweet.relevancy_second,tweet.relevancy_third]
            tweet.voted_relevancy=max(((item, rel_list.count(item)) for item in set(rel_list)), key=lambda a: a[1])[0]
        #print('Relevance')

    if(((tweet.relevancy != 'none') & (tweet.relevancy != '') & (tweet.relevancy != None)) & ((tweet.sentiment != 'none') & (tweet.sentiment != '') & (tweet.sentiment != None))
        & ((tweet.relevancy_second != 'none') & (tweet.relevancy_second != '') & (tweet.relevancy_second != None)) & ((tweet.sentiment_second != 'none') & (tweet.sentiment_second != '')& (tweet.sentiment_second != None))
        & ((tweet.relevancy_third != 'none') & (tweet.relevancy_third != '') & (tweet.relevancy_third != None)) & ((tweet.sentiment_third != 'none') & (tweet.sentiment_third != '') & (tweet.sentiment_third != None))):
        tweet.labeled = True
    tweet.save()


def retrain():
    correctionData = CorrectionData.objects.all()
    trainSet= []
    for item in correctionData:
        trainSet.append({'label' : item.relevancy, 'text' :item.text })

    filter = Filter(r"C:\Users\Tarek Abdelhakim\workspace\DjangoWebProject1",item.stock.strip(),True)
    filter.GetBestClassifier(trainSet)
    

@login_required
def news(request):
    #Select Today's News 
    from django.utils import timezone
    #today =datetime.datetime.strftime(timezone.now(),"%Y-%m-%d")
    #newsList=Opinion.objects.extra(where={"`pub_date` LIKE CONCAT(  '%%',  '"+today+"',  '%%' ) and `source` != 'twitter.com' "}).values()

    #changed, news page was not openning during Eud vacation / doesn't return values
    newsList=Opinion.objects.exclude(id=1).order_by('-id')[0:50].values();
    
    News =[]
    for newsItem in newsList:
        n=NewsItem()
        n.link = newsItem['media_url']
        n.title = newsItem['text']
        News.append(n)
    """Renders the news page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/news.html',
        context_instance = RequestContext(request,
        {
            'title':'News',
            'News':News,
        })
    )

def runPriceCrawling():
    urlstr = 'http://www.marketstoday.net/markets/%D8%A7%D9%84%D8%B3%D8%B9%D9%88%D8%AF%D9%8A%D8%A9/Companies/1/ar/'
    fileHandle = urllib.request.urlopen(urlstr)
    html = fileHandle.read()
    soup = BeautifulSoup(html)
    #print(soup)
    from pytz import timezone
    localtz = timezone('UTC')
    time_in_site=localtz.localize(parse(soup.findAll('span', attrs={'class':'tradhour'})[0].text.split('\n', 1)[1].split(" :")[1].replace('(local time)\r\n','',1)));

    urlstr_tasi = 'http://www.marketstoday.net/markets/%D8%A7%D9%84%D8%B3%D8%B9%D9%88%D8%AF%D9%8A%D8%A9/Index-Performance/1/ar/'
    fileHandle_tasi = urllib.request.urlopen(urlstr_tasi)
    html_tasi = fileHandle_tasi.read()
    soup_tasi = BeautifulSoup(html_tasi)
    item = StocksPrices()
    item.stock_id=3
    item.close=soup_tasi.find('span', attrs={'class':'valuetxt'}).text.replace(',','')
    item.time=time_in_site
    try:
        item.save()
    except:
        pass

    for b in soup.findAll('tr', attrs={'class':'symbolflip'})[1:]:
        try:
            stockname=b.find('a', attrs={'class':'jTip'}).text
            stocks = Stocks.objects.filter(marketstoday_name=stockname)[0]
            close=b.findAll('td')[1].text.replace(',','')
            open=b.findAll('td')[2].text.replace(',','')
            max=b.findAll('td')[3].text.replace(',','')
            min=b.findAll('td')[4].text.replace(',','')
            vol=b.findAll('td')[8].text.replace(',','')
            print(stocks.stock)
            print(close)
            item = StocksPrices()
            item.stock_id=stocks.stock_id
            item.close=close
            item.open=open
            item.max=max
            item.min=min
            item.volume=vol
            item.time=time_in_site
            item.save()
        except:
            pass
    return True

def runNewsCrawling():
    newsstock = Stocks.objects.filter(stock='none')[0].stock_id
    # id = 1 twitter, id = 20 error RSS
    for news_site_object in Sources.objects.exclude(id__in=[1,20]):
        news_site=news_site_object.source
        source_id=news_site_object.source_id
        try:
            rssPage = urllib.request.urlopen(news_site)
            rssFeed = minidom.parse(rssPage)
            news_counter=0
            for item in rssFeed.getElementsByTagName("item"):
                a=item.getElementsByTagName("link")[0]
                for num in range(0,2):
                    try:
                        if a.childNodes[num].nodeValue != ' ':
                            opmedia=a.childNodes[num].nodeValue
                    except:
                        pass
                if not Opinion.objects.exclude(source_id=1).filter(media_url=opmedia).exists():
                    news_counter=news_counter+1;
                    Op = Opinion()
                    Op.media_url=opmedia
                    Op.source_id=news_site_object.source_id
                    a=item.getElementsByTagName("title")[0]
                    for num in range(0,2):
                        try:
                            if a.childNodes[num].nodeValue != ' ':
                                Op.text=a.childNodes[num].nodeValue
                        except:
                            pass
                    Op.pub_date=timezone.now()
                    try:
                        a=item.getElementsByTagName("pubDate")[0]
                        for num in range(0,2):
                            if a.childNodes[num].nodeValue != ' ':
                                Op.pub_date=a.childNodes[num].nodeValue
                    except:
                        pass
                    Op.twitter_id = randint(0,99999999999999999)
                    Op.tweeter_id = ''
                    Op.created_at = timezone.now()
                    Op.user_followers_count = 0
                    Op.stock_id = newsstock
                    Op.labeled = False
                    #Op.p_relevancy = None
                    #Op.p_sentiment = None
                    #Op.p_question = None
                    Op.question = None
                    print("saved")
                    Op.save()
            print(str(news_site)+ ' ' + str(news_counter))
        except:
            print(str(news_site)+ ' ERROR')
            pass
    #Classifing
    for news in Opinion.objects.filter(stock_id=5).exclude(source_id=1).exclude(labeled=True):
        Labeled_flag = False
        for stocks in Stocks.objects.exclude(stock_id__in=[1,2,4,5]):
            word_not_found_flag = True;
            for word_list in stocks.synonym.replace(')','').replace('(','').split(' or '):
                word = word_list.replace('+',' ').split()
                for w in range(0,len(word)-1):
                    if len(word[w]) < 2:
                        word[w]='random_text_to_exclude_this_word_list'
                if all(x1 in news.text for x1 in word) and word_not_found_flag:
                    Op = Opinion()
                    Op.twitter_id = news.twitter_id
                    Op.tweeter_id = news.tweeter_id;
                    Op.created_at = news.created_at
                    Op.pub_date = news.pub_date;
                    Op.text = news.text
                    Op.stock_id = stocks.stock_id
                    Op.source_id = news.source_id;
                    Op.labeled = False
                    Op.media_url = news.media_url
                    #Op.p_relevancy = None
                    #Op.p_sentiment = None
                    #Op.p_question = None
                    Op.question = None
                    word_not_found_flag = False;
                    Labeled_flag = True;
                    print(word)
                    print(news.text)
                    try:
                        Op.save()
                    except:
                        pass
        news.labeled=True;
        news.save();


@login_required
def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        context_instance = RequestContext(request,
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.datetime.now().year,
        })
    )

@login_required
def about(request):         
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        context_instance = RequestContext(request,
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.datetime.now().year,
        })
    )

def login_user_proto(request):
    oauth = OAuth1(consumerKey, client_secret=consumerSecret)
    r = requests.post(url=request_token_url, auth=oauth)
    credentials = urllib_parse.parse_qs(r.content.decode("utf-8"))
    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]
    
    #full_auth_url = authenticate_url + '?oauth_token=' + resource_owner_key
    #authorization_url = oauth.authorization_url(base_authorization_url)
    full_auth_url = base_authorization_url + '?oauth_token=' + resource_owner_key
    request.session['request_token'] = str(resource_owner_key)
    return redirect(full_auth_url)    
    
    '''
    if request.method == 'POST':
        #logout(request)
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/home_proto')
                #return HttpResponseRedirect('/about/')
    return redirect('/')
    '''
def twitter_authenticated(request):
    if request.method == 'GET':

        accessToken = request.GET['oauth_token']
        accessTokenVerifier = request.GET['oauth_verifier']
        accessTokenSecret = request.session.get('request_token', None)
        '''
        oauth = OAuth1(consumerKey, client_secret=consumerSecret)
        r = requests.post(url=request_token_url, auth=oauth)
        credentials = urllib_parse.parse_qs(r.content.decode("utf-8"))
        resource_owner_key = credentials.get('oauth_token')[0]
        resource_owner_secret = credentials.get('oauth_token_secret')[0]
    
        oauth = OAuth1(client_key=consumerKey, client_secret=consumerSecret, resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret)
        r = requests.post(url=access_url, auth=oauth)
        
        access_token_from_url = urllib_parse.parse_qs(r.content.decode("utf-8"))
        
        
        username = access_token_from_url['screen_name']
        '''
        '''
        oauth = OAuth1(consumerKey, client_secret=consumerSecret)
        r = requests.post(url=request_token_url, auth=oauth)
        credentials = urllib_parse.parse_qs(r.content.decode("utf-8"))
        resource_owner_key = credentials.get('oauth_token')[0]
        resource_owner_secret = credentials.get('oauth_token_secret')[0]
        #from requests_oauthlib import OAuth1Session
        oauth = OAuth1(consumerKey,
                              client_secret=consumerSecret,
                              resource_owner_key=resource_owner_key,
                              resource_owner_secret=resource_owner_secret,
                              verifier=accessTokenVerifier)
        
        #oauth_tokens = oauth.fetch_access_token(access_url)
        r = requests.post(url=access_url, auth=oauth)
        
        access_token_from_url = urllib_parse.parse_qs(r.content.decode("utf-8"))
        username = access_token_from_url['screen_name']
        #password = oauth_tokens['oauth_token_secret']
        password = accessTokenSecret
        '''
        oauth = OAuth1(consumerKey,
                       client_secret=consumerSecret,
                       resource_owner_key=accessToken,
                       resource_owner_secret=accessTokenSecret,
                       verifier=accessTokenVerifier)

        r = requests.post(url=access_url, auth=oauth)
        credentials = urllib_parse.parse_qs(r.content.decode("utf-8"))
        resource_owner_key = credentials.get('oauth_token')[0]
        resource_owner_secret = credentials.get('oauth_token_secret')[0]
        '''
        See http://requests-oauthlib.readthedocs.org/en/latest/oauth1_workflow.html#workflow-example-showing-use-of-both-oauth1-and-oauth1session
        >>> protected_url = 'https://api.twitter.com/1/account/settings.json'
        
        >>> # Using OAuth1Session
        >>> oauth = OAuth1Session(client_key,
                                  client_secret=client_secret,
                                  resource_owner_key=resource_owner_key,
                                  resource_owner_secret=resource_owner_secret)
        >>> r = oauth.get(protected_url)
        
        >>> # Using OAuth1 auth helper
        >>> oauth = OAuth1(client_key,
                           client_secret=client_secret,
                           resource_owner_key=resource_owner_key,
                           resource_owner_secret=resource_owner_secret)
        >>> r = requests.get(url=protected_url, auth=oauth)
        '''        
        
        t = Twitter(auth=OAuth(resource_owner_key,resource_owner_secret, consumerKey,consumerSecret))
        results = t.account.verify_credentials()
        username = results['screen_name']
        #password = resource_owner_secret
        #user = authenticate(username=username, password=password)
        from app.models import User
        
        try:
            user = User.objects.get(username=username)
            request.session['user_authenticated'] = True
            return redirect('/home_proto')
            
        except User.DoesNotExist:
            return render(
                            request,
                            'app/signup.html',
                            context_instance = RequestContext(request,
                            {
                                'twitter_username':username,
                            }))
    

        
def login_user(request):
    if request.method == 'POST':
        #logout(request)
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/home')
                #return HttpResponseRedirect('/about/')
    return redirect('/register')

def twitter_register(request):
    if request.method == 'POST':
        from app.forms import UserForm
        user_form = UserForm(data=request.POST)
        #user_form.data['username'] = request.session.get('twitter_username', None)
        from app.models import User
        if user_form.is_valid() :
            user = user_form.save()

            user.set_password(user.password)
            user.save()
            new_user = User()
            new_user.username = request.POST['username']
            new_user.email = request.POST['email']
            new_user.save()
            #request.session['message'] = 'registration done please login'
            return redirect("/home_proto")
            #return render(request, 'app/site_layout.html', {'message':'registration done please login'})
        else:
            request.session['error'] = user_form.errors
            #return redirect("/prototype")
            return render(request, 'app/signup.html', {'error':user_form.errors})

def register(request):
    if request.method == 'POST':
        from app.forms import UserForm
        user_form = UserForm(data=request.POST)

        if user_form.is_valid() :
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            request.session['message'] = 'registration done please login'
            return redirect("/")
            #return render(request, 'app/site_layout.html', {'message':'registration done please login'})
        else:
            request.session['error'] = user_form.errors
            return redirect("/")
           #return render(request, 'app/site_layout.html', {'error':user_form.errors})
    else:
        return redirect("/")

@ajax
def get_last_100(request):
    stock = request.POST['query']
    classifier = request.POST['classifier']
    content_return = []
    print("Start get_stock_rel_info")
    stock_id=Stocks.objects.filter(stock=stock)[0].stock_id
    
    try:
        cor_count = Correction.objects.filter(stock_id=stock_id).filter(classifier=classifier,segment=1,correction=True).values()[0]['counter']
    except:
        cor_count = 1
    try:
        inc_count = Correction.objects.filter(stock_id=stock_id).filter(classifier=classifier,segment=1,correction=False).values()[0]['counter']
    except:
        inc_count = 1
    
    content_return.append(['Correct', cor_count])
    content_return.append(['Incorrect', inc_count])
    return content_return;


def train_filters(request):
    save_path = 'data'
    FilterStocks.Filter.init(save_path)

    evalutaions = FilterStocks.Filter.evaluate(save_path)
    response = {
    'status': 'Trained',
    'evaluation': evalutaions
    }
    return JsonResponse(response)
    #return HttpResponse("Trained...<br/>Evaluation accuracies:<br/>" + json.dumps(evalutaions))

def evaluate_filters(request):
    #load_path = 'data'
    #evalutaions = FilterStocks.Filter.evaluate(load_path)
    #print(evalutaions)
    evalutaions={}
    latest=Evaluation.objects.all().aggregate(Max('time'))['time__max']
    ev=Evaluation.objects.filter(time=latest).select_related('stock');
    for e in ev:
        evalutaions[e.stock.stock]=e.evaluation;

    response = {
        'evaluation': evalutaions
    }
    return JsonResponse(response)
    #return json.dumps(evalutaions)
    #return HttpResponse("Evaluation accuracies:<br/>" + json.dumps(evalutaions))


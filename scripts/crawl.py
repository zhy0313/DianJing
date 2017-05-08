#coding:utf-8   
import sys
import requests
import json
import time
import random
import datetime

import redis


# the main page refreh api 
#Url = "http://www.toutiao.com/api/pc/feed/?category=__all__&utm_source=toutiao"
#Url = "http://www.toutiao.com/api/pc/feed/?category=news_hot&utm_source=toutiao&widen=1"

Url = "http://www.toutiao.com/api/pc/feed/?category=%s&utm_source=toutiao&widen=1&max_behot_time=%s&max_behot_time=%s&tadrequire=true&as=A135C940DF6BE90&cp=590FEB5EB9E01E1"

cat = int(sys.argv[1])
start_date = sys.argv[2]
delta_days = int(sys.argv[3])

r = redis.StrictRedis(host='localhost', port=6379, db=0)
start_timestamp = datetime.datetime.strptime(start_date,"%Y%m%d").strftime("%s")
end_timestamp = (datetime.datetime.strptime(start_date,"%Y%m%d") - datetime.timedelta(days=delta_days)).strftime("%s")
timestamp = start_timestamp
cats = ["news_tech","news_society","news_entertainment","news_sports","news_car","news_finance"]

def process():
    global timestamp
    toutiao_data = requests.get(Url%(cats[cat],timestamp,timestamp)).text
    data = json.loads(toutiao_data)

    if data.get("message") == "false":
        return 

    articals = data.get("data")
    #timestamp = (datetime.datetime.fromtimestamp(int(timestamp)) - datetime.timedelta(minutes=15)).strftime("%s")
    timestamp = data.get("next").get("max_behot_time")

    for artical in articals:
        if not artical.get("group_id") or not artical.get("title") or not artical.get("abstract"):
            continue
        key = artical.get("group_id")
        #print key,artical.get("title")
        r.set(key,artical)

def crawl():
    count = 0 
    while(int(timestamp) > int(end_timestamp)):
        print "crawl num #[%d] with time stamp [%s]"%(count,timestamp)
        gap = random.randint(4,7)
        time.sleep(gap)
        process()
        count += 1

if __name__ == "__main__":
    crawl()

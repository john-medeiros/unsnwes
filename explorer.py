import feedparser
import urllib.request as urllib2
import sqlite3
import hashlib

url = 'https://www.bbc.com/portuguese/topics/cvjp2jr0k9rt'

feed = feedparser.parse(url)

feed

import os
import logging
import logging.handlers
import feedparser
import urllib.request as urllib2
import sqlite3
import hashlib
import datetime
import time

class RSSContent:

  def __init__(self):
    self.__creation_time = datetime.datetime.now()
    self.__feed_title = None
    self.__feed_subtitle = None
    self.__feed_link = None
    self.__feed_entry_id = None
    self.__feed_entry_title = None
    self.__feed_entry_published_datetime = None
    self.__feed_entry_link = None
    self.__feed_entry_raw = None
    self.__feed_entry_id_hash = None

  @property
  def creation_time(self):
      return self.__creation_time

  @creation_time.setter
  def creation_time(self, value):
      self.__creation_time = str(value)

  @property
  def feed_title(self):
      return self.__feed_title

  @feed_title.setter
  def feed_title(self, value):
      self.__feed_title = str(value)

  @property
  def feed_subtitle(self):
      return self.__feed_subtitle

  @feed_subtitle.setter
  def feed_subtitle(self, value):
      self.__feed_subtitle = str(value)

  @property
  def feed_link(self):
      return self.__feed_link

  @feed_link.setter
  def feed_link(self, value):
      self.__feed_link = str(value)     

  @property
  def feed_entry_id(self):
      return self.__feed_entry_id

  @property
  def feed_entry_id_hash(self):
      return self.__feed_entry_id_hash

  @feed_entry_id.setter
  def feed_entry_id(self, value):
      self.__feed_entry_id = str(value)
      self.__feed_entry_id_hash = hashlib.md5(str(value).encode()).hexdigest()

  @property
  def feed_entry_title(self):
      return self.__feed_entry_title

  @feed_entry_title.setter
  def feed_entry_title(self, value):
      self.__feed_entry_title = str(value)

  @property
  def feed_entry_published_datetime(self):
      return self.__feed_entry_published_datetime

  @feed_entry_published_datetime.setter
  def feed_entry_published_datetime(self, value):
      self.__feed_entry_published_datetime = str(value)

  @property
  def feed_entry_link(self):
      return self.__feed_entry_link

  @feed_entry_link.setter
  def feed_entry_link(self, value):
      self.__feed_entry_link = str(value) 

  @property
  def feed_entry_raw(self):
      return self.__feed_entry_raw

  @feed_entry_raw.setter
  def feed_entry_raw(self, value):
      self.__feed_entry_raw = str(value) 

  def to_db(self):
    conn = None
    cur = None
    try:
      conn = None
      conn = sqlite3.connect('local.db')
      cur = conn.cursor()
      cur.execute("""INSERT INTO rss_feed_collected (feed_title,feed_subtitle,feed_link,feed_entry_id,feed_entry_title,feed_entry_published_datetime,feed_entry_link,feed_entry_raw,creation_time,feed_entry_id_hash) VALUES (?,?,?,?,?,?,?,?,?,?);""", (self.feed_title,self.feed_subtitle,self.feed_link,self.feed_entry_id,self.feed_entry_title,self.feed_entry_published_datetime,self.feed_entry_link,self.feed_entry_raw,self.creation_time,self.__feed_entry_id_hash))
      conn.commit()
    except Exception as e:
      raise e
    finally:
      conn.close()
      #cur.close()
  
  def feed_exists(self)-> bool:
    conn = None
    cur = None
    rv = None
    try:
      conn = None
      conn = sqlite3.connect('local.db')
      cur = conn.cursor()
      cur.execute('SELECT COUNT(*) FROM rss_feed_collected WHERE feed_entry_id_hash = ?', (self.feed_entry_id_hash,))
      row_count=cur.fetchone()[0]
      if row_count>0:
        rv=True
      else:
        rv=False
      conn.commit()
    except Exception as e:
      raise e
    finally:
      conn.close()
      return rv

def init():
    # É executada no começo do programa
    logFileName='.'+os.path.basename(__file__).replace('.py', '.log')
    logger = logging.getLogger()
    fh = logging.handlers.RotatingFileHandler(logFileName, encoding='utf-8')
    fh.setLevel(logging.INFO)#no matter what level I set here
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    #formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(lineno)s - %(funcName)s() - %(message)s')
    fh.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(fh)
    logging.info('--------------------------------------------------------------------------------------------------------------------------------')
    logging.info('Início do processamento com PID: ' + str(os.getpid()))
  
def collect(url):
  try:

    logging.info('Collecting url:' + url)
    feed = feedparser.parse(url)

    for post in feed.entries:
      feed_data_received = RSSContent()

      if 'title' in feed.feed:
        feed_data_received.feed_title = feed['feed']['title']

      if 'subtitle' in feed.feed:
        feed_data_received.feed_subtitle = feed['feed']['subtitle']

      if 'link' in feed.feed:
        feed_data_received.feed_link = feed['feed']['link']

      if hasattr(post, 'link')==1:
        feed_data_received.feed_entry_link = post.link      

      if hasattr(post, 'id')==1:
            feed_data_received.feed_entry_id = post.id

      
      
      feed_data_received.feed_entry_published_datetime = datetime.datetime.fromtimestamp(time.mktime(post.published_parsed))
      feed_data_received.feed_entry_raw = post
      feed_data_received.feed_entry_title = post.title
      if not feed_data_received.feed_exists():
        feed_data_received.to_db()
  except Exception as e:
    logging.error(e)
    logging.exception(e)
    raise e

init()
url ='https://www.valor.com.br/financas/rss'

collect(url)



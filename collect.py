import os
import logging
import logging.handlers
import feedparser
import urllib.request as urllib2
import sqlite3
import hashlib
import datetime
import time
import sys
import signal

MIN_PYTHON = (3, 7)

if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

run=False

def keep_running()-> bool:
  return run

def sigterm_handler(signal, frame):
    global run
    run = False
    logging.info('Finalização solicitada pelo usuário...')
    logging.info('Aguarde a finalização da execução da linha atual.')
    print('Finalização solicitada pelo usuário...')
    sys.exit(0)

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
      self.__feed_entry_id_hash = hashlib.md5(str(value).encode()).hexdigest()

  @property
  def feed_entry_raw(self):
      return self.__feed_entry_raw

  @feed_entry_raw.setter
  def feed_entry_raw(self, value):
      self.__feed_entry_raw = str(value) 

  def to_db(self)-> None:
    conn = None
    cur = None
    try:
      db_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'db','local.db')
      conn = None
      conn = sqlite3.connect(db_path)
      cur = conn.cursor()
      cur.execute("""INSERT INTO rss_feed_collected (feed_title,feed_subtitle,feed_link,feed_entry_title,feed_entry_published_datetime,feed_entry_link,feed_entry_raw,creation_time,feed_entry_id_hash) VALUES (?,?,?,?,?,?,?,?,?);""", (self.feed_title,self.feed_subtitle,self.feed_link,self.feed_entry_title,self.feed_entry_published_datetime,self.feed_entry_link,self.feed_entry_raw,self.creation_time,self.__feed_entry_id_hash))
      conn.commit()
    except Exception as e:
      logging.exception(e)
      raise e
    finally:
      conn.close()
      del conn
      del cur
      #cur.close()
  
  def feed_exists(self)-> bool:
    conn = None
    cur = None
    rv = None
    try:
      db_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'db','local.db')
      conn = None
      conn = sqlite3.connect(db_path)
      cur = conn.cursor()
      cur.execute('SELECT COUNT(*) FROM rss_feed_collected WHERE feed_entry_id_hash = ?', (self.feed_entry_id_hash,))
      row_count=cur.fetchone()[0]
      if row_count>0:
        rv=True
      else:
        rv=False
      conn.commit()
    except Exception as e:
      logging.exception(e)
      raise e
    finally:
      conn.close()
      del conn
      del cur
      return rv

def collect(url):
  row_count_read = 0
  row_count_write = 0
  try:
    feed = feedparser.parse(url)
    for post in feed.entries:
      feed_data_received = RSSContent()
      if 'title' in feed.feed:
        feed_data_received.feed_title = feed['feed']['title']
      if 'subtitle' in feed.feed:
        feed_data_received.feed_subtitle = feed['feed']['subtitle']
      if 'link' in feed.feed:
        feed_data_received.feed_link = feed['feed']['link']
      else:
        feed_data_received.feed_link = url
      feed_data_received.feed_entry_link = post.link
      #if hasattr(post, 'published_parsed')==1:
      feed_data_received.feed_entry_published_datetime = datetime.datetime.fromtimestamp(time.mktime(post.published_parsed))
      #else:
        #print('Não possui published_parsed')
      feed_data_received.feed_entry_raw = post
      feed_data_received.feed_entry_title = post.title
      if not feed_data_received.feed_exists():
        feed_data_received.to_db()
        row_count_write = row_count_write + 1
      
      row_count_read = row_count_read + 1
      del feed_data_received    
  except Exception as e:
    logging.error('Ocorreu um erro ao obter conteúdo RSS. Site: ' + str(url))
    logging.exception(e)
    raise e
  finally:
    return row_count_read, row_count_write

def get_sites():
  sites=['']
  #file = open("sites.txt", "r") 
  sites_to_watch=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sites.txt')
  with open(sites_to_watch) as f:
    next(f)
    for line in f: 
      sites.append(line.strip())
  return sites

def init():
    # É executada no começo do programa
    #logFileName='./log/'+os.path.basename(__file__).replace('.py', '.log')
    logFileName=os.path.join(os.path.dirname(os.path.abspath(__file__)),'log',os.path.basename(__file__).replace('.py', '.log'))
    logger = logging.getLogger()
    fh = logging.handlers.RotatingFileHandler(logFileName, encoding='utf-8', maxBytes=1)
    fh.setLevel(logging.INFO)#no matter what level I set here
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    #formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(lineno)s - %(funcName)s() - %(message)s')
    fh.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(fh)
    logging.info('--------------------------------------------------------------------------------------------------------------------------------')
    logging.info('Início do processamento com PID: ' + str(os.getpid()))
    print('Logging into: ' + str(logFileName))
    global run
    run = True

def main():
    try:
      signal.signal(signal.SIGTERM, sigterm_handler)
      signal.signal(signal.SIGABRT, sigterm_handler)
      signal.signal(signal.SIGINT, sigterm_handler)

      init()

      session_rr=0
      session_rw=0

      while keep_running():
        s=get_sites()
        logging.info('Quantidade de sites para busca de RSS: ' + str(len(s)))
        for item in s:
          if keep_running() == False:
            break
          if len(item)>0:
            if item[0]=='#':
              logging.info('Ignorando site: [' + str(item) + '].')
              continue
          else:
            continue
          rr,rw=collect(item) 
          session_rr=session_rr+rr
          session_rw=session_rw+rw
          logging.info('Coletando do site: [' + str(item) + ']. Notícias lidas: [' + str(rr) + ']. Notícias gravadas: [' + str(rw) + '].')
        logging.info('Notícias lidas: [' + str(session_rr)+ '] Notícias gravadas: [' + str(session_rw) + ']')
        time.sleep(10)
    except Exception as e:
      logging.error('Ocorreu um erro ao executar coleta de RSS.')
      logging.exception(e)
      raise e

if __name__ == '__main__':
    main()
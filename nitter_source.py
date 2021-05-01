import requests, feedparser
from bs4 import BeautifulSoup as bs


class NitterSource:

    # nitter rss : twitter hashtag
    # https://github.com/zedeus/nitter/wiki/Instances
    feed_nitter_domain = [  "nitter.cc", 
                            "nitter.kavin.rocks", 
                            "nitter.eu", 
                            "nitter.42l.fr", 
                            "nitter.exonip.de", 
                            "nitter.pussthecat.org",
                            "nitter.nixnet.services",
                            "nitter.tedomum.net",
                            "twitr.gq"
                        ]
    feed_nitter_base = "https://{domain}/search/rss?f=tweets&q=%23{hashtag}"
    feed_nitter_keys = ["summary_detail", "value"]

    @classmethod
    def __getFeedData(cls, url, keys):
        """ Generic feed parser. take out author, published, text and imagelist """
        try:
            res = requests.get(url, timeout=5)
            list_ = []
            if res.status_code == 200:
                feed = feedparser.parse(res.text)
                for entries in feed["entries"]:
                    #print(entries)
                    d = {}
                    html = entries   # keys = ["content", 0, values]
                    for key in keys:
                        html = html[key] # html = entries["content"][0]["values"]
                    soup = bs(html, "html.parser")
                    d["published"] = entries["published"]
                    d["author"] = entries["author"]
                    d["text"] = soup.text
                    d["imgs"] = []
                    for i in soup.find_all('img'):
                        d["imgs"].append(i["src"])
                    list_.append(d)
                return list_
            else:
                print(url + " : ERROR : in data retrieval :  " + str(res.status_code))
                return None
        except requests.exceptions.Timeout:
            print(url + " : ERROR : TIMEOUT")
            return None


    @classmethod
    def getNitterFeed(cls, hashtag):
        """ hashtag and username both """
        url = None
        for domain in cls.feed_nitter_domain:
            url = cls.feed_nitter_base.format(domain=domain, hashtag = hashtag)
            ret = cls.__getFeedData(url, cls.feed_nitter_keys)
            if ret == None:
                continue
            return ret
        return None
    

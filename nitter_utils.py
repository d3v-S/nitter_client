
import sys, requests, io, pickle
from PIL import Image


class Utils:

    ##################
    # private methods:
    ##################
    @classmethod
    def __resizeImageWidth(cls, img, width):
        wpercent = (width/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        return img.resize((width,hsize), Image.ANTIALIAS)

    @classmethod
    def __resizeImageHeight(cls, img, height):
        hpercent = (height/float(img.size[1]))
        wsize = int((float(img.size[0]*float(hpercent))))
        return img.resize((wsize, height), Image.ANTIALIAS)


    #######################
    # Image Manipulation
    #######################
    # keep aspect ratio same on resizing downloaded data.
    @classmethod
    def resizeImageKeepingAspectRatio(cls, img_data, limit_width, limit_height=None):
        img = Image.open(img_data)
        w = img.size[0]
        h = img.size[1]
        if w > limit_width:
            img = cls.__resizeImageWidth(img, limit_width)
            bio = io.BytesIO()
            img.save(bio, format="PNG")
            return bio.getvalue()
        else:
            if limit_height != None:
                if h > limit_height:
                    img = cls.__resizeImageHeight(img, limit_height)
                    bio = io.BytesIO()
                    img.save(bio, format="PNG")
                    return bio.getvalue()
        return img_data.getvalue()


    #############
    # debugging:
    #############
    
    DEBUG = False
    ERROR = True
    @classmethod
    def dbg(cls, string):
        if cls.DEBUG:
            print(string)

    @classmethod
    def err(cls, str):
        if cls.ERROR:
            print(string)


    
    ##############
    # downloading 
    ##############
    
    @classmethod
    def __getUrl(cls, url):
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                return res
            else:
                cls.err("URL: " + url + " : error = response code : " + str(res.status_code))
            return None
        except requests.exceptions.Timeout:
            cls.err("URL: " + url + " : error = timeout")
            return None
            
    
    @classmethod
    def loadUrl(cls, url, url_cache=None):
        if url_cache:
            if url in url_cache.keys():
                return url_cache[url]
            else:
                data = cls.__getUrl(url)
                url_cache[url] = data
                return data
        else:
            data = cls.__getUrl(url)
            return data


    #################
    # pickling object
    #################
    @classmethod
    def objToFile(cls, obj, filename):
        dbfile = open(filename, 'wb')    
        pickle.dump(obj, dbfile)                     
        dbfile.close()

    @classmethod
    def fileToObj(cls, filename):
        dbfile = open(filename, 'rb')     
        db = pickle.load(dbfile)
        dbfile.close()
        return db
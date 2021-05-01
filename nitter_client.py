from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys, requests, io, time
from PIL import Image
import itertools

from nitter_utils import Utils
from nitter_source import NitterSource



###########################
#
# GLOBAL VARIABLES
#
############################

MAXIMUM_WINDOW_WIDTH = 1000 #pixel
MAIN_WINDOW_WIDGET = None
MAIN_WINDOW_STATUS = None




qssStyle = '''
QPushButton[name='btn_author']{
    border-radius: 10px;
    height: 32px;
    font-weight: bold;
    font-family:"Fira Code", sans-serif;
    font-size: 25px;
    border: 3px solid #aaa;
    padding: 10px;
}

QPushButton[name='btn_author']:hover{
    border: 5px solid #ff0;
}

QLabel[name='label_timestamp']{
    font-size: 12px;
    font-family: monospace;

}

QLabel[name='label_desc']{
    font-size: 16px;
    font-family: "Fira Code";
    margin-bottom: 50px;
    border-top: 1px dashed #aaa;
    border-left: 0px;
    border-right: 0px;
    border-bottom: 10px solid #ddd;
    padding-bottom: 20px;
    padding-top: 10px;
    margin-top: 10px
}

WTweet{
    border-style: solid;
    border-color: "#ccc";
    border-width: 5px;
}


'''






#
# Misc
# 
class Misc:
    @classmethod
    def loadImageFromUrl(cls, url, max_width, max_height,  url_cache=None):
        """ load image from URL. will return image_label """
        pixmap = QPixmap()
        image_label = QLabel()
        data = Utils.loadUrl(url, url_cache)
        if data != None:
            data = Utils.resizeImageKeepingAspectRatio(io.BytesIO(data.content), max_width, max_height)
            pixmap.loadFromData(data)
        image_label.setPixmap(pixmap)
        return image_label



#
# Widget for One Tweet
# 
class WTweet(QWidget):
    def __init__(self, tweet_dict, max_image_width, max_image_height, url_cache=None):
        """ tweet_dict = [author, text, published, imgs]"""

        super(WTweet, self).__init__()
        
        Utils.dbg(tweet_dict)

        # name this object:
        self.setProperty("name", "wtweet")
        

        # author
        self.label_author = QPushButton()
        self.label_author.setText(tweet_dict["author"].strip())
        self.label_author.clicked.connect(self.addToTab)
        self.label_author.setProperty('name', "btn_author")

        # time of publish
        self.label_timestamp = QLabel()
        self.label_timestamp.setText(tweet_dict["published"].strip())
        self.label_timestamp.setAlignment(Qt.AlignRight)
        self.label_timestamp.setProperty('name', "label_timestamp")


        # description:
        self.label_desc = QLabel()
        self.label_desc.setWordWrap(True)
        self.label_desc.setText(tweet_dict["text"].strip())
        self.label_desc.setProperty("name", "label_desc")

            
        # author and timestamp in single line:
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignCenter)
        hbox.addWidget(self.label_author, 50)
        hbox.addWidget(self.label_timestamp, 50)
        frame = QFrame()
        frame.setLayout(hbox)

        # set main widget layout
        lmain = QVBoxLayout()
        lmain.addWidget(frame)

        # adding images:
        for img in tweet_dict["imgs"]:
            lmain.addWidget(Misc.loadImageFromUrl(img, max_image_width, max_image_height, url_cache))

        lmain.addWidget(self.label_desc)
        lmain.setProperty("name", "lmain")
        self.setMaximumWidth(MAXIMUM_WINDOW_WIDTH)
        self.setLayout(lmain)

    @pyqtSlot()
    def addToTab(self):
        val = str(self.label_author.text())
        MAIN_WINDOW_WIDGET.to_download.append(val)

        # list_ = NitterSource.getNitterFeed(val)
        # MAIN_WINDOW_WIDGET.main_tab.addTab(WFeed(list_, int(MAIN_WINDOW_WIDGET.width/3), int(MAIN_WINDOW_WIDGET.height/3)), val)




#
# Complete Column of WTweets.
#
class WFeed(QScrollArea):
    def __init__(self, list_tweet, max_image_width, max_image_height):
        super(WFeed, self).__init__()
        self.list_tweet = list_tweet
        self.max_image_height = max_image_height
        self.max_image_width =max_image_width
        self.setWidgetResizable(True)
        content_widget = QWidget()
        self.setWidget(content_widget)
        vbox = QVBoxLayout(content_widget)
        self.vbox = vbox
        for tweet in reversed(list_tweet):
            vbox.addWidget(WTweet(tweet, max_image_width, max_image_height, MAIN_WINDOW_WIDGET.img_url_cache))
        
    def update(self, list_tweet):
        # difference between new and old list
        # using itertools becasuse list of dict
        diff = list(itertools.filterfalse(lambda x: x in self.list_tweet, list_tweet)) + list(itertools.filterfalse(lambda x: x in list_tweet, self.list_tweet))
        print("diff: " + str(len(diff)))
        print(diff)
        # for i in reversed(range(self.vbox.count())):
        #     self.vbox.itemAt(i).widget().setParent(None)
        for tweet in reversed(diff):
            self.vbox.addWidget(WTweet(tweet, self.max_image_width, self.max_image_height, MAIN_WINDOW_WIDGET.img_url_cache))
        self.list_tweet = list_tweet
        


#
# Widget with input, submit button and time for updating.
# -- used to enter hashtags/usernames.
#
class WInputFeedName(QWidget):
    def __init__(self, parent):
        
        global MAIN_WINDOW_STATUS

        super(WInputFeedName, self).__init__()
        self.parent = parent

        self.btn = QPushButton("Submit")
        self.input = QLineEdit()

        # status whether downloading or not
        self.status = QLabel()
        self.status.setText("Nothing.")
        MAIN_WINDOW_STATUS = self.status

        # add tab when clicked submit.
        self.btn.clicked.connect(self.addTabToParent)
        
        # time of update, in Minutes:
        self.cb = QComboBox()
        self.cb.addItem("1")
        self.cb.addItem("5")
        self.cb.addItem("15")
        self.cb.addItem("30")
        self.cb.addItem("60")
        self.cb.addItem("120")
        self.cb.addItem("3600")
        self.cb.currentIndexChanged.connect(self.changeUpdateInterval)

        
        # layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.input, 70)
        hbox.addWidget(self.status,10)
        hbox.addWidget(self.btn, 10)
        hbox.addWidget(self.cb, 10)

        self.setLayout(hbox)
    

    @pyqtSlot()
    def addTabToParent(self):
        val = self.input.text().strip()
        MAIN_WINDOW_WIDGET.to_download.append(val)
        # list_ = NitterSource.getNitterFeed(val)
        # self.parent.main_tab.addTab(WFeed(list_, int(self.parent.width/3), int(self.parent.height/3)), val)


    @pyqtSlot()
    def changeUpdateInterval(self):
        self.parent.update_interval = int(self.cb.currentText())


#
# Thread
#
class Downloader(QThread):
    downloaded = pyqtSignal()
    def __init__(self, parent = None):
        super(Downloader, self).__init__(parent)
    
    def run(self):
        while(1):
            if len(MAIN_WINDOW_WIDGET.to_download) > 0:
                MAIN_WINDOW_STATUS.setText("Downloading.")
                val = MAIN_WINDOW_WIDGET.to_download.pop()
                list_ = NitterSource.getNitterFeed(val)
                if list_ != None:
                    MAIN_WINDOW_WIDGET.downloaded.append((val, list_))
                    for item in list_:
                        for url in item["imgs"]:
                            Utils.loadUrl(url, MAIN_WINDOW_WIDGET.img_url_cache)
                    self.downloaded.emit()
                else:
                    MAIN_WINDOW_STATUS.setText("Error. Nitter.")
            time.sleep(1)

#
# Thread
#
class Updater(QThread):
    updated = pyqtSignal()
    def __init__(self, parent = None):
        super(Updater, self).__init__(parent)
    
    def run(self):
        while(1):
            for i in range(MAIN_WINDOW_WIDGET.main_tab.count()):
                val = MAIN_WINDOW_WIDGET.main_tab.tabText(i)
                MAIN_WINDOW_STATUS.setText("refreshing ...")    
                list_ = NitterSource.getNitterFeed(val)
                if list_ == None:
                    MAIN_WINDOW_STATUS.setText("Error. Nitter")
                    continue
                present = False
                for index, item in enumerate(MAIN_WINDOW_WIDGET.updated):
                    if item[0] == val:
                        present = True
                        MAIN_WINDOW_WIDGET.updated[index] = (val, list_)
                        break
                if not present:
                    MAIN_WINDOW_WIDGET.updated.append((val, list_))
                for item in list_:
                    for url in item["imgs"]:
                        Utils.loadUrl(url, MAIN_WINDOW_WIDGET.img_url_cache)
                self.updated.emit()
            time.sleep(MAIN_WINDOW_WIDGET.update_interval*60)


# Main window class.
class NitterClient(QWidget):
    def __init__(self, list_tweet = None, width=1200, height=1000):
        
        global MAIN_WINDOW_WIDGET

        super(QWidget, self).__init__()
        self.width = width
        self.height = height
        self.update_interval = 1 
        self.img_url_cache = {}
       
        #  input and stuff
        self.input = WInputFeedName(self)
                
        # tabs
        self.main_tab = QTabWidget()
        self.main_tab.setTabsClosable(True)
        self.main_tab.tabCloseRequested.connect(lambda index: self.main_tab.removeTab(index))
        
        # main window layout
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignCenter) 
    
        wid = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(self.input)
        vbox.addWidget(self.main_tab)
        wid.setLayout(vbox)
        wid.setMaximumWidth(MAXIMUM_WINDOW_WIDTH + 100)

        hbox.addWidget(wid)
        self.setLayout(hbox)
        self.setStyleSheet(qssStyle)

        # set it so that we can access it from anywhere, without passing it.
        MAIN_WINDOW_WIDGET = self
        
        # thread.
        self.to_download = []
        self.downloaded = []
        self.thread = Downloader()
        self.thread.downloaded.connect(self.updateDownloadUI)
        self.thread.start()

        self.updated = []
        self.thread1 = Updater()
        self.thread1.updated.connect(self.updateRefreshUI)
        self.thread1.start()
        

        # self.worker2 = Downloader()
        # self.worker2.start()
        # self.worker2.downloaded.connect(self.updateUI)


        #self.setMaximumWidth(MAXIMUM_WINDOW_WIDTH + 100)

    def updateDownloadUI(self):
        print("Downloaded....")
        if (len(self.downloaded) > 0):
            MAIN_WINDOW_STATUS.setText("UI updating...")
            (val, list_) = self.downloaded.pop()
            self.main_tab.addTab(WFeed(list_, int(self.width - 50), int(self.height/2)), val)
            MAIN_WINDOW_STATUS.setText("Done.")

    def updateRefreshUI(self):
        print("updating ui..")
        if len(self.updated) > 0:
            MAIN_WINDOW_STATUS.setText("re-build tab")
            (val, list_) = self.updated.pop()
            for i in range(self.main_tab.count()):
                if val == self.main_tab.tabText(i):
                    qtab = self.main_tab.widget(i)
                    qtab.update(list_)
            MAIN_WINDOW_STATUS.setText("Done.")

        


app = QApplication(sys.argv)
screen = NitterClient()
screen.show()
sys.exit(app.exec_())
    
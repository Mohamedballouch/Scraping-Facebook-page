from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options
import sys
import time
import calendar
from bs4 import BeautifulSoup as bs
import json
import re
import requests
from settings import BROWSER_EXE, FIREFOX_BINARY,PROFILE
import datefinder
import re

GECKODRIVER="geckodriver.exe"

delay=5


def scarp_post():
    
    """
    URL = 'https://www.facebook.com/pg/hespress/posts'
    page = requests.get(URL).content
    """
    browser = webdriver.Firefox(executable_path=GECKODRIVER,firefox_profile=PROFILE,)
    
    browser.get('https://www.facebook.com/pg/hespress/posts')
    

    # Scroll down depth-times and wait delay seconds to load
    # between scrolls
    depth=8
    for scroll in range(depth):
    
        # Scroll down to bottom
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
    
        # Wait to load page
        time.sleep(delay)
    
    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source
    
    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')
    
    
    time.sleep(delay)
    
    
    
    def _extract_post_id(item):
      
            
        links =item.select('a[href^="/Hespress/"]')
            
        post_id = ""
        
        for postLink in links:
                if "/Hespress/posts" in postLink['href']:
                    
                    p = re.compile("/Hespress/posts/(\d+)")
                    post_id=p.findall(postLink['href'])[0]
                    
    
                elif  "/Hespress/photos"  in postLink['href']:
                    
                    post_id = re.findall(r'\d+', postLink['href'])[0]
                   
    
                elif  "/Hespress/videos" in postLink['href']:
                    
                    post_id = re.findall(r'\d+', postLink['href'])[0]
                    
                    
       
        return post_id
    
    
    def _extract_post_text(item):
        actualPosts = item.find_all(attrs={"data-testid": "post_message"})
        text = ""
        if actualPosts:
            for posts in actualPosts:
                paragraphs = posts.find_all('p')
                text = ""
                for index in range(0, len(paragraphs)):
                    text += paragraphs[index].text
        return text
    
    def _extract_link(item):
        global post_type
    
        
        links =item.select('a[href^="/Hespress/"]')
        
        
        link = ""
        
        for postLink in links:
                if "/Hespress/posts" in postLink['href']:
                    link = "www.facebook.com"+postLink['href']
               
                    post_type='Article'
                    
                elif  "/Hespress/photos"  in postLink['href']:
                    link = "www.facebook.com"+postLink['href']
            
                    post_type='Image'
                    
                elif  "/Hespress/videos" in postLink['href']:
                    link = "www.facebook.com"+postLink['href']
             
                    post_type='Video'
                
        return link,post_type
    
    
    
    def _extract_image(item):
        
        image = ""
        if post_type=='Video':
            postvideos = item.find_all(class_="_3chq")
            
            for postvid in postvideos:
            
                if postvid.get('src') is not None:
                    image = postvid.get('src')
                else:
                    image=''
        else:
            postPictures = item.find_all(class_="scaledImageFitWidth img")
          
            
            for postPicture in postPictures:
           
                if postPicture.get('src') is not None:
                    image = postPicture.get('src')
                else:
                    image=''
                    
        return image
    
    
    
    def _extract_shares(item):
        
        postShares = item.find_all(class_="_4vn1")
    
        shares = ""
        
        for postShare in postShares:
            
            y=postShare.find_all( class_="_3rwx _42ft")
            if not y :
                
                shares = "0"
    
            else:
                for cc in postShare.find_all(class_="_3rwx _42ft"):
                    x = cc.string
                    x = x.split(">", 1)
                    share = x[0].split()[0]
              
                    if "K"  in share:
                        
                        shares=int(float(share.replace('K', ''))*1000)
        
                    elif  "M" in share:
                            
                        shares=int(float(share.replace('M', ''))*1000000)
        
                    else:
                        shares=share
        
        return shares
    
    
    
    def _extract_caption(item):
        
        postCaptions = item.find_all(class_="_52c6")
    
        caption = "" 
        
        for postCaption in postCaptions:
            
            if not postCaption.find_all('span') :
                
                caption = ""
    
            else:
                for Cap in postCaption.find_all('span'):
    
                    caption=Cap.string
                    print(caption)
        
        return caption
    
    
    
    
    def _extract_comments(item):
        
        postComments = item.find_all(class_="_4vn1")
    
        comments = ""
    
        for comment in postComments:
            
    
            r=comment.find_all( class_="_3hg- _42ft")
            if not r :
                
                comments = "0"
            else :
                for cc in comment.find_all(class_="_3hg- _42ft"):
    
                    m=cc.string
                    m = m.split(">", 1)
                    comt = m[0].split()[0]
                    
                    if "K"  in comt:
                        
                        comments=int(float(comt.replace('K', ''))*1000)
        
                    elif  "M" in comt:
                            
                        comments=int(float(comt.replace('M', ''))*1000000)
        
                    else:
                        comments=comt
    
        
        return comments
    
    
    
    def _extract_type(item):
    
        likes_p = item.find_all("a", attrs = {'class' : '_1n9l'})
    
        
        post_likes=""
        for lik in likes_p:
    
            if "Like" in lik["aria-label"]:
    
                x = lik["aria-label"]
        
                x = x.split(">", 1)
                likes = x[0].split()[0]
         
                if "K"  in likes:
                    
                    post_likes=int(float(likes.replace('K', ''))*1000)
    
                elif  "M" in likes:
                        
                    post_likes=int(float(likes.replace('M', ''))*1000000)
    
                else:
                    post_likes=likes 
    
    
    
        return post_likes
    
    
    
    #posts = browser.find_elements_by_class_name("userContentWrapper")
    
    def  _extract_dates(item):
        ti_Posts = item.find_all(class_="_5ptz")
        
        
        for post in  ti_Posts:
            # Creating a time entry.
    
            matches=list(datefinder.find_dates(post['title']))
            
            if len(matches) > 0:
                # date returned will be a datetime.datetime object.
                date1 = str(matches[0]).split(":", 1)[0]
                date = re.sub('[- ]', '', date1)
    
            else:
                date='no dates found'
          
                
        return date
            
      
        
    k= bs_data.find_all(class_="_5pcr userContentWrapper")
    postBigDict = list()
    
    
    time.sleep(delay)
    
    for item in k:
    
            
        postDict = dict()
        
        postDict['PostId'] = _extract_post_id(item)
        postDict['Date'] = _extract_dates(item)
        postDict['Message'] = _extract_post_text(item)
        postDict['Caption'] =_extract_caption(item)
        postDict['Link'],postDict['Post_type'] = _extract_link(item)
        postDict['Image'] = _extract_image(item)
        postDict['Likes']=_extract_type(item)
        postDict['Shares'] = _extract_shares(item)
        postDict['Comments']=_extract_comments(item)
        
        #Add to check
        postBigDict.append(postDict)
        with open('./postBigDict.json','w', encoding='utf-8') as file:
            file.write(json.dumps(postBigDict, ensure_ascii=False).encode('utf-8').decode())
    
    
    
########## *************** Scrap facebook posts every hour **** ######################



import os
  
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
#from apscheduler.scheduler import Scheduler
import six

sched = BlockingScheduler()


sched.add_job(scarp_post, 'cron',hour='*',minute=29)

sched.start()  
        
        
    
    

#!/usr/bin/env python
import urllib
import random
#from gi.repository import Gio
#import time
import cv2
import numpy as np
import Image
from matplotlib import pyplot as plt
import os

import urllib2
import re, json, time,hashlib, random
import MultipartPostHandler
from gevent import pool
from gevent import monkey
from urllib2 import URLError, HTTPError

#monkey.patch_all()


MIN_MATCH_COUNT = 10



print('Starting')
#settings = Gio.Settings.new("org.gnome.desktop.background")

#scheduler = sched.scheduler(time.time, time.sleep)

 
def grab_pano():

    base_url = "https://maps.googleapis.com/maps/api/streetview?size=640x640&fov=60"
    base_map_url = "https://maps.googleapis.com/maps/api/staticmap?"

    heading1 = "&heading=0"
    heading2 = "&heading=40"
    key = "&key=AIzaSyAZmBxtk886_pPO44tWt0UW9LNoYtlrnVE"

    picPath1 = "/home/ross/Desktop/python_code/Street_View_Background/pic1.jpg"
    picPath2 = "/home/ross/Desktop/python_code/Street_View_Background/pic2.jpg"
    mapPath = "/home/ross/Desktop/python_code/Street_View_Background/map.jpg"
    panoPath = "/home/ross/Desktop/python_code/Street_View_Background/pano.jpg"

    print(picPath1)
    while True: 

        while True:
            rand_lon = 360*(random.random()-0.5)
                
            if (rand_lon > -105 and rand_lon < -80):
                break

        while True:
            rand_lat = 360*(random.random()-0.5)
        
            if (rand_lat < 45 and rand_lat > 30):
                break
        

        longitude, latitude, address = get_address(rand_lat, rand_lon)
        longitude  = "{:.9f}".format(longitude)
        latitude =  "{:.9f}".format(latitude)
        
       # print(address)
       # print(latitude)
       # print(longitude)
       
        location = "&location=" + latitude + "," + longitude
        url1 = base_url + heading1 + location + key
        print(url1)

        urllib.urlretrieve(url1,picPath1)
        img1 = cv2.imread(picPath1)
            

        url_map = base_map_url + "&center=" + latitude + "," + longitude + "&zoom=5&size=150x150"
        urllib.urlretrieve(url_map, mapPath)
        mapImg = cv2.imread(mapPath)


        # check to see if image exists
        sum = int(img1[0][0][0]) + int(img1[0][0][1]) + int(img1[0][0][2])
        
        print("\n\n")
        if sum != 678:
            break;


    
    url2 = base_url + heading2 + location + key
    print(url2)
    urllib.urlretrieve(url2,picPath2)
    img2 = cv2.imread(picPath2)

    img3 = stich_photos(img1,img2,mapImg);





def stich_photos(img1,img2,mapImg):
    panoPath = "/home/ross/Desktop/python_code/Street_View_Background/pano.jpg"

    gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

    img1 = cv2.cvtColor(img1,cv2.COLOR_BGR2RGB)
    img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2RGB)

    sift = cv2.xfeatures2d.SIFT_create()

    kp1, des1 = sift.detectAndCompute(gray1,None)
    kp2, des2 = sift.detectAndCompute(gray2,None)


    # FLANN parameters
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)   # or pass empty dictionary

    flann = cv2.FlannBasedMatcher(index_params,search_params)
 
    matches = flann.knnMatch(des1,des2,k=2)


    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

    if len(good)>MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

        M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC,5.0)

        h1,w1 = gray1.shape
        h2,w2 = gray2.shape 
        h3,w3,d3 = mapImg.shape
        warp = cv2.warpPerspective(img2,M,(w1+w2,h1))

        final = np.zeros((h1,w1+w2,3), np.uint8)
        final[:h1,:w1+w2] = warp
        final[:h1,:w1] = img1
        final[h1-h3:h1, w1+w2-w3:w1+w2] = mapImg

        img3 = Image.fromarray(final,'RGB')
        img3.save(panoPath)
        
        return img3

    else:
        print "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT)
        return 0

    
        


def get_address(latitude,longitude):

    url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng=%f,%f&sensor=false&language=zh-CN' % (latitude, longitude)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(), urllib2.HTTPRedirectHandler())
    
    print(url)

    try:
        str_content = opener.open(url).read()
    except HTTPError, e:
        print 'Error code: ', e.code
        time.sleep(36)
        return get_address()
    except URLError, e:
        print e.reason
        time.sleep(36)
        return get_address()

    if str_content:
        content = json.loads(str_content)
        if content['status'] == 'OK':
            address = content['results'][0]['formatted_address']               
            longitude = content['results'][0]['geometry']['location']['lng']
            latitude =  content['results'][0]['geometry']['location']['lat']
            return (longitude, latitude, address)
        else:
            print content['status'].encode('utf-8') + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            time.sleep(36) # This is due to the 2500/24h limit.
            return get_address()
 




#time.sleep(5)

#settings.set_string("picture-uri", "/home/ross/Desktop/python_code/Street_View_Background/pano.jpg")
#os.system("gsettings set org.gnome.desktop.background picture-uri /home/ross/Desktop/python_code/Street_View_Background/pano.jpg")

#print('Start:' , time.time())
#scheduler.enter(10, 1, grab_pano(),None)
#scheduler.run()
if __name__ == "__main__":
    grab_pano()

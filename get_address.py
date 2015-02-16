import urllib2
import re, json, time,hashlib, random
import MultipartPostHandler
from gevent import pool
from gevent import monkey
from urllib2 import URLError, HTTPError

monkey.patch_all()

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
            print('Test')
            address = content['results'][0]['formatted_address']               
            longitude = content['results'][0]['geometry']['location']['lng']
            latitude =  content['results'][0]['geometry']['location']['lat']
            return (longitude, latitude, address)
        else:
            print content['status'].encode('utf-8') + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            time.sleep(36) # This is due to the 2500/24h limit.
            return get_address()

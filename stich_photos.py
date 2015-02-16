import cv2
import numpy as np
import Image
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 10

def stich_photos(img1,img2):
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
        warp = cv2.warpPerspective(img2,M,(w1+w2,h1))

        final = np.zeros((h1,w1+w2,3), np.uint8)
        final[:h1,:w1+w2] = warp
        final[:h1,:w1] = img1

        img3 = Image.fromarray(final,'RGB')
        img3.save('pano.jpg')
        
        return img3

    else:
        print "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT)
        return 0

    
        
 


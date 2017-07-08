#!/usr/bin/python
#coding: utf-8
import os
import cv2
import Porn

__NormWidth__ = 240

def __load_image(filepath):
    try:
        img = cv2.imread(filepath)
        print filepath
        WHRatio = float(img.shape[0]) / img.shape[1]
        Nimg = cv2.resize(img, (__NormWidth__, int(__NormWidth__ * WHRatio)))
        return Nimg
    except Exception, e:
        print "[!] ", e, " [!]"

def test(rootpath):
    a = 0
    c = 0
    for f in os.listdir(rootpath):
        filepath = os.path.join(rootpath, f)
        if not os.path.isdir(filepath):
            print f
            if f != '.DS_Store':
                img = __load_image(filepath)
                if P.classify(img):
                    c += 1
                a += 1
    print float(c) * 100 / a , "%"

if __name__ == '__main__':
    P = Porn.PornClassifier()
    test("data/test")
    test("data/false")
    #test("data")

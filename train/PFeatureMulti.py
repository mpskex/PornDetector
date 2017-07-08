#!/usr/bin/python
#coding: utf-8

import os
import cv2
import numpy
import Func
import Porn
from multiprocessing import Pool


__NormWidth__ = 240

def SubProc(Func, img, label, num, length):
    print "%3.2f %% \t (%4d/%4d)"%(float(num) * 100 / length, num, length)
    return Func.GetFeature(img, num), label

def __load_image(filepath):
    try:
        img = cv2.imread(filepath)
        print filepath
        WHRatio = float(img.shape[0]) / img.shape[1]
        Nimg = cv2.resize(img, (__NormWidth__, int(__NormWidth__ * WHRatio)))
        return Nimg
    except Exception, e:
        print "[!] ", e, " [!]"

def __load_images(rootpath):
    imglist = []
    filelist = os.listdir(rootpath)
    for f in filelist:
        filepath = os.path.join(rootpath, f)
        if f != '.DS_Store':
            if not os.path.isdir(filepath):
                Nimg = __load_image(filepath)
                imglist.append(Nimg)
    print "[*]  Images Loaded!"
    return imglist

def SaveAsMat(label, VecList, filename):
    with open(filename, 'w') as f:
        vstr = ''
        for i in range(len(VecList)):
            vstr += str(label[i])
            vstr += ' '
            for j in range(len(VecList[i])):
                vstr += str(VecList[i][j]) + ' '
            vstr += '\n'
        print vstr
        f.write(vstr)
    f.close()

def LoadMat(filename):
    label = []
    VecList = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            label.append(int(line.split(' ')[0]))
            FeatureVec = []
            for elem in line.split(' ')[1:]:
                if elem != '\n':
                    FeatureVec.append(float(elem))
            VecList.append(FeatureVec)
        f.close()
    return label, VecList

def run(P, truepath, falsepath):
    IHandler = Func.PornImageHandler()
    truelist = __load_images(truepath)
    falselist = __load_images(falsepath)
    #   Multi Proc
    VecList = []
    label = []
    result = []
    num = 1
    pool = Pool()
    for img in truelist:
        result.append(pool.apply_async(SubProc, args = (IHandler, img, 1, num, len(truelist) + len(falselist), )))
        num += 1
    for img in falselist:
        result.append(pool.apply_async(SubProc, args = (IHandler, img, 0, num, len(truelist) + len(falselist), )))
        num += 1
    pool.close()
    pool.join()
    for r in result:
        print r.get()[1]
        VecList.append(r.get()[0])
        label.append(r.get()[1])
    return label, VecList

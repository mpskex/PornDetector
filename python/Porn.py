#!/usr/bin/python
#coding: utf-8
import os
import math
import cv2
import numpy as np
import Func
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import platform
pltfm = platform.system()
if pltfm == 'Linux':
    from libsvm_linux import svmutil as svm
elif pltfm == 'Darwin':
    from libsvm_mac import svmutil as svm
else:
    raise "Unsupported Platform!"

class PornClassifier:
    def __init__(self):
        self.modelpath = "model.m"

    def classify(self, img):
        IHandler = Func.PornImageHandler()
        #img = cv2.imread(filename)
        num = 1
        VecList = []
        label = []
        #   将图片特征向量
        VecList.append(IHandler.GetFeature(img))
        label.append(1)
        num += 1
        if os.path.exists(self.modelpath):
            model = svm.svm_load_model(self.modelpath)
        else:
            self.train()
        p_labs, p_acc, p_vals = svm.svm_predict(label, VecList, model, '-b 1')
        print p_labs, p_acc, p_vals
        if p_labs[0] > 0.5:
            return True
        else:
            return False 
    def __SubProc(self, Func, VecList, label, img, l, num, length):
        #   将图片特征向量
        VecList.append(Func.GetFeature(img, num))
        label.append(l)
        print "%.2f %% (%4d/%4d)"%(float(num) * 100 / length, num, length)
    
    def ExtractFeature(self, truepath, falsepath):
        num = 1
        VecList = []
        label = []
        self.truelist = self.__load_images(truepath)
        self.falselist = self.__load_images(falsepath)
        IHandler = Func.PornImageHandler()
        #   训练正样本
        for img in self.truelist:
            self.__SubProc(IHandler, VecList, label, img, 1, num, len(self.truelist)+len(self.falselist))
            num += 1 
        #   训练负样本
        for img in self.falselist:
            self.__SubProc(IHandler, VecList, label, img, 0, num, len(self.truelist)+len(self.falselist))
            num += 1
        print "[*]  Created Process Pool!"
        print len(VecList) , " ", len(label)
        return label, VecList

    def __SaveAsMat(self, label, VecList, filename):
        with open(filename, 'w') as f:
            vstr = ''
            for i in range(len(VecList)):
                vstr += str(label[i])
                vstr += ' '
                for j in range(len(VecList[i])):
                    vstr += str(j+1) + ':' + str(VecList[i][j]) + ' '
                vstr += '\n'
            print vstr
            f.write(vstr)
        f.close()

    def train(self, label, VecList):
        #self.__SaveAsMat(label, VecList, "prob.mat")
        #model = svm.svm_train(label, VecList, '-s 0 -t 0 -c 15 -g 0.01 -b 1')
        model = svm.svm_train(label, VecList, '-s 1 -t 2 -c 2 -g 0.0001 -b 1 -h 0 ')
        svm.svm_save_model(self.modelpath, model)
        print "model trained..."

    def crossvalid(self, label, VecList):
        result = svm.svm_train(label, VecList, '-s 1 -t 2 -c 2 -g 0.0001 -b 1 -h 0 -v 5')
        print result



if __name__ == '__main__':
    '''
    Porn = PornClassifier("test/IsPorn", "test/NotPorn", "inter/")
    rootpath = "test/test"
    '''
    Porn = PornClassifier("data/IsPorn", "data/NotPorn", "inter/")
    #Porn.train()
    
    c = 0
    a = 0
    rootpath = "data/false"
    for f in os.listdir(rootpath):
        filepath = os.path.join(rootpath, f)
        if not os.path.isdir(filepath):
            print f
            if f != '.DS_Store':
                if Porn.classify(filepath):
                    c += 1
                a += 1
    print float(c) * 100 / a , "%"
    #Porn.classify("test.jpg")
    
#!/usr/bin/python
#coding: utf-8

import Func
import Porn
import PFeatureMulti

def SubProc(Func, img, label, num, length):
    print "%3.2f %% \t (%4d/%4d)"%(float(num) * 100 / length, num, length)
    return Func.GetFeature(img), label

if __name__ == '__main__':
    P = Porn.PornClassifier()
    #label, VecList = PFeatureMulti.run("data/IsPorn", "data/NotPorn")
    #PFeatureMulti.SaveAsMat(label, VecList, 'prob.mat')
    label, VecList = PFeatureMulti.LoadMat('prob.mat')
    P.crossvalid(label, VecList)
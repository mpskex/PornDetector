#!/usr/bin/python
#coding: utf-8

import Porn
import Func
import PFeatureMulti

if __name__ == '__main__':
    P = Porn.PornClassifier()
    label, VecList = PFeatureMulti.run(P, "data/IsPorn", "data/NotPorn")
    PFeatureMulti.SaveAsMat(label, VecList, 'prob.mat')
    #label, VecList = PFeatureMulti.LoadMat('prob.mat')
    P.train(label, VecList)
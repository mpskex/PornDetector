#!/usr/bin/python
#coding: utf-8

import Func
import Porn


def SaveAsMat(label, VecList, filename):
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

def LoadMat(filename):
    label = []
    VecList = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            label.append(int(line.split(' ')[0]))
            FeatureVec = []
            for elem in line.split(' ')[1:]:
                if elem != '\n':
                    FeatureVec.append(float(elem.split(':')[-1]))
            VecList.append(FeatureVec)
        f.close()
    return label, VecList


def run(P):
    label, VecList = P.ExtractFeature()
    return label, VecList
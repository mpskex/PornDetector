#!/usr/bin/python
#coding: utf-8
import math
import numpy as np
import cv2

class PornImageHandler:
    def __init__(self):
        pass
    #   重新使用论文中方法实现
    #   《一种融合方法的皮肤检测技术》
    #   后来发现论文中的方法并没有什么用
    #   直接根据PornDetective模块的参数重新实现了一下
    def __BinSeg(self, img):
        #   转换为HSV颜色模型  
        #   将文件转换问HSV空间，考虑光照使用HSV模型
        #   OpenCV中转换HSV使用COLOR_BGR2HSV_FULL
        HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)
        #   使用阈值控制筛选内容
        Lower = np.array([0, 57, 10])
        #   由于opencv对HSV色彩空间进行了压缩，所以轴上值全部用八位二进制表示
        #   cH = H * 255 / 360      cS = S * 255     cV = V * 255
        #   对应上界是（经过换算）24.791   58.65   173.4
        #   原   0,57,10 -> 24, 174, 255
        #   现   0,20,10 -> 24, 174, 255
        Upper = np.array([24, 174, 255])
        mask = cv2.inRange(HSV, Lower, Upper)
        SkinOnly = cv2.bitwise_and(img, img, mask=mask)
        return SkinOnly

    #   计算颜色占比
    #   计算二值化图像中计算非黑色区域占比
    def __CalcRatio(self, SkinOnly):
        count = 0
        S_map = np.zeros((SkinOnly.shape[0], SkinOnly.shape[1]))
        for h in range(SkinOnly.shape[0]):
            for w in range(SkinOnly.shape[1]):
                if (SkinOnly[h][w] == np.matrix([0, 0, 0])).all():
                    #   黑色为非皮肤区域
                    S_map[h][w] = 0
                else:
                    #   白色为皮肤区域
                    count += 1
                    S_map[h][w] = 255
        return S_map, count
    
    #   可视化Smap
    #   使用了切割好了label segment表
    def __VisualSmap(self, S_map, area_list, name):
        area_label = np.zeros((S_map.shape[0], S_map.shape[1], 3))
        label = np.zeros(3)
        for pixels in area_list:
            #   对是皮肤的区域创建新标签
            #   使用中国剩余定理，为了能够容纳更大的标签数量
            #   由于会出现公约数整除的情况，那时三通道的值又为0了，导致下面死循环
            #   之后使用的标签不需要是可视化的
            label[0] = (label[0] - 11)%255
            label[1] = (label[1] - 31)%255
            label[2] = (label[2] - 57)%255
            #   如果出现了等于零的情况，那么就再进行一次叠加
            if (label == 0).all():
                label[0] = (label[0] - 11)%255
                label[1] = (label[1] - 31)%255
                label[2] = (label[2] - 57)%255
            for cord in pixels:
                area_label[cord[0]][cord[1]] = label
        #cv2.imwrite('inter/' + name + "_AreaLabel" + ".bmp", area_label)
        return
                

    #   判断皮肤区域
    #   基于区域生长的图片区域标定方法
    #   判定邻接是使用的十字邻接法
    def __SkinArea(self, S_map):
        area_label = np.zeros((S_map.shape[0], S_map.shape[1]), np.uint8)
        count = 0
        area = 1
        area_list = []
        pixels = []
        seeds = []
        for h in range(S_map.shape[0]):
            for w in range(S_map.shape[1]):
                #   map里面没有标签
                if area_label[h][w] == 0 and S_map[h][w] == 255:
                    seeds.append((h,w))
                    if not pixels == []:
                        area_list.append(pixels)
                    count += 1
                    #print "\tlabel's area is " + str(area)
                    #   计算面积
                    #print "label found! " + str(count)
                    #   初始化新标签中变量
                    area = 1
                    pixels = []
                    pixels.append((h,w))
                else:
                    continue
                #   已经有标签
                while seeds:
                    #   弹出第一个元素
                    y, x = seeds.pop(0)
                    #   找到了之后标记
                    area_label[y][x] = 1
                    for m in range(3):
                        for n in range(3):
                            if y+m-1>=0 and y+m-1<S_map.shape[0] and x+n-1>=0 and x+n-1<S_map.shape[1]:
                                if S_map[y+m-1][x+n-1] == 255:
                                    if abs(m-1)<1 or abs(n-1)<1:
                                        if area_label[y+m-1][x+n-1]==0:
                                            area += 1
                                            #   找到之后标记
                                            area_label[y+m-1][x+n-1] = 1
                                            pixels.append((y+m-1, x+n-1))
                                            seeds.append((y+m-1, x+n-1))
        return area_list

    #   去除过小的标签
    def __Reducedlist(self, area_list):
        R_area_list = []
        for pixels in area_list:
            if len(pixels)>40:
                R_area_list.append(pixels)
                #print len(pixels)
        return R_area_list

    #   以Segment面积大小对Segment排序
    def __SegmentSort(self, area_list):
        return sorted(area_list, key = lambda x : len(x), reverse = True)

    #   检查分段是否有重合
    def __CheckSegment(self, area_list):
        count = 0
        for p in area_list:
            for q in area_list:
                if not p==q:
                    for a in p:
                        for b in q:
                            if a==b:
                                count += 1
        return count
    
    #   计算距离
    def __Dist(self, a, b):
        return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

    #   这里是简化的距离矩阵
    #   通过计算主体与其他区块的区域关系来达到提高特征区分度和计算效率的作用
    #   计算分段之间的距离，并存储到矩阵中
    #   使用的是挪步法，或者是优先法
    #   待讨论
    def __SegmentDist(self, area_list, S_map):
        if len(area_list) > 1:
            DistVector = np.zeros((len(area_list) - 1), np.float32)
            i = 0
            for j in range(len(area_list)):
                #   自己到自己的距离没有意义
                #   上三角矩阵存储距离
                if i!=j:
                    #   这里计算距离
                    #   关于算法中算子移动的问题还需要仔细考虑
                    TempMinDist = self.__Dist((0,0),(S_map.shape[0],S_map.shape[1]))
                    #   如何取点，需要商榷
                    p = area_list[i][1]
                    q = area_list[j][1]
                    #   让程序正确进入循环
                    OrgDist = TempMinDist + 1
                    #   交替迭代直到p，q之间距离最小
                    while OrgDist > TempMinDist:
                        OrgDist = self.__Dist(p, q)
                        for m in range(3):
                            for n in range(3):
                                if abs(m-1)<1 or abs(n-1)<1:
                                    if p[0]+m-1>=0 and p[0]+m-1<S_map.shape[0] and p[1]+n-1>=0 and p[1]+n-1<S_map.shape[1]:
                                        if S_map[p[0]+m-1][p[1]+n-1] == 255:
                                            t = self.__Dist((p[0]+m-1,p[1]+n-1),q)
                                            #print 'Dist' + str(t)
                                            if TempMinDist > t:
                                                TempMinDist = t
                                                #   p,q交换
                                                p = (p[0]+m-1, p[1]+n-1)
                        for m in range(3):
                            for n in range(3):
                                if abs(m-1)<1 or abs(n-1)<1:
                                    if q[0]+m-1>=0 and q[0]+m-1<S_map.shape[0] and q[1]+n-1>=0 and q[1]+n-1<S_map.shape[1]:
                                        if S_map[q[0]+m-1][q[1]+n-1] == 255:
                                            t = self.__Dist((q[0]+m-1,q[1]+n-1),p)
                                            #print 'Dist' + str(t)
                                            if TempMinDist > t:
                                                TempMinDist = t
                                                q = (q[0]+m-1, q[1]+n-1)
                    #   存储距离矩阵
                    DistVector[j-1] = TempMinDist
            #print DistVector
            return DistVector
        else:
            return np.matrix([0])
    '''
    #   完全距离矩阵计算
    #   计算分段之间的距离，并存储到矩阵中
    #   使用的是挪步法，或者是优先法
    #   待讨论
    def __SegmentDist(self, area_list, S_map):
        DistMatrix = np.zeros((len(area_list), len(area_list)), np.float32)
        for i in range(len(area_list)):
            for j in range(len(area_list)):
                #   自己到自己的距离没有意义
                #   上三角矩阵存储距离
                if not i<=j:
                    #   这里计算距离
                    #   关于算法中算子移动的问题还需要仔细考虑
                    TempMinDist = self.__Dist((0,0),(S_map.shape[0],S_map.shape[1]))
                    #   如何取点，需要商榷
                    p = area_list[i][1]
                    q = area_list[j][1]
                    #   让程序正确进入循环
                    OrgDist = TempMinDist + 1
                    #   交替迭代直到p，q之间距离最小
                    while OrgDist > TempMinDist:
                        OrgDist = self.__Dist(p, q)
                        #print '____' + str(i) + '->' + str(j) + '____'
                        #print '++++' + str(p) + '->' + str(q) + '++++'
                        for m in range(3):
                            for n in range(3):
                                if abs(m-1)<1 or abs(n-1)<1:
                                    if p[0]+m-1>=0 and p[0]+m-1<S_map.shape[0] and p[1]+n-1>=0 and p[1]+n-1<S_map.shape[1]:
                                        if S_map[p[0]+m-1][p[1]+n-1] == 255:
                                            t = self.__Dist((p[0]+m-1,p[1]+n-1),q)
                                            #print 'Dist' + str(t)
                                            if TempMinDist > t:
                                                TempMinDist = t
                                                #   p,q交换
                                                p = (p[0]+m-1, p[1]+n-1)
                        for m in range(3):
                            for n in range(3):
                                if abs(m-1)<1 or abs(n-1)<1:
                                    if q[0]+m-1>=0 and q[0]+m-1<S_map.shape[0] and q[1]+n-1>=0 and q[1]+n-1<S_map.shape[1]:
                                        if S_map[q[0]+m-1][q[1]+n-1] == 255:
                                            t = self.__Dist((q[0]+m-1,q[1]+n-1),p)
                                            #print 'Dist' + str(t)
                                            if TempMinDist > t:
                                                TempMinDist = t
                                                q = (q[0]+m-1, q[1]+n-1)
                    #   存储距离矩阵
                    DistMatrix[i][j] = TempMinDist
        return DistMatrix
        '''
    def __StructVector(self, count, SkinOnly, SR_area_list, DistVector):
        FeatureVector = []
        #   加入比例
        FeatureVector.append(float(count) / (SkinOnly.shape[0] * SkinOnly.shape[1]))
        #   加入区块数量
        FeatureVector.append(len(SR_area_list))
        #   加入距离矩阵平均值
        if DistVector.shape[0] > 0:
            FeatureVector.append(np.mean(DistVector))
            FeatureVector.append(math.sqrt(np.var(DistVector)))
        else:
            FeatureVector.append(math.sqrt(SkinOnly.shape[0]**2 + SkinOnly.shape[1]**2))
            FeatureVector.append(100)
        #   加入第一块大小占皮肤区域比例
        if SR_area_list!=[]:
            FeatureVector.append(float(len(SR_area_list[0])) / (SkinOnly.shape[0] * SkinOnly.shape[1]))
        else:
            #空list
            FeatureVector.append(0)
        return FeatureVector

    def GetFeature(self, img):
        FeatureVector = []
        SkinOnly = self.__BinSeg(img)
        S_map, count = self.__CalcRatio(SkinOnly)
        #cv2.imwrite('inter/' + name + "_Smap" + ".bmp", S_map)
        area_list = self.__SkinArea(S_map)
        R_area_list = self.__Reducedlist(area_list)
        SR_area_list = self.__SegmentSort(R_area_list)
        for p in SR_area_list:
            #print "<area> is " + str(len(p))
            pass
        #   可视化
        #self.__VisualSmap(S_map, SR_area_list, name)
        #print 'Rep in ' + str(self.__CheckSegment(R_area_list))
        DistVector = self.__SegmentDist(SR_area_list, S_map)
        #print DistVector
        FeatureVector = self.__StructVector(count, SkinOnly, SR_area_list, DistVector)
        return FeatureVector

def __load_images(self, rootpath):
    imglist = []
    filelist = os.listdir(rootpath)
    for f in filelist:
        filepath = os.path.join(rootpath, f)
        if not os.path.isdir(filepath):
            try:
                img = cv2.imread(filepath)
            except:
                print "[!]--Read Image Failed!--[!]"
    return imglist

if __name__ == '__main__':
    __NormWidth__ = 240
    IHandler = PornImageHandler()
    img = cv2.imread('data/false/COCO_val2014_000000000192.jpg')
    WHRatio = float(img.shape[0]) / img.shape[1]
    Nimg = cv2.resize(img, (__NormWidth__, int(__NormWidth__ * WHRatio)))
    print IHandler.GetFeature(img)

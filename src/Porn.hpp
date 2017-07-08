#pragma once
//------------------------------------
//  A method to detect porn pictures
//  Author: mpsk
//  Beijing University of Technology
//  http://
//------------------------------------
#include <vector>
#include <queue>
#include <iostream>
#include <opencv2/opencv.hpp>

using namespace cv;
using namespace std;

class CV_Point
{
    public:
        CV_Point(int x, int y)
        {
            this->x = x;
            this->y = y;
        }
        int x,y;
};
/*
    重新使用论文中方法实现
    《一种融合方法的皮肤检测技术》
    后来发现论文中的方法并没有什么用
    直接根据PornDetective模块的参数重新实现了一下
*/
class PornImageHandler
{
    private:
        //  成员
        double skin_ratio;
        Mat img, hsvimg, s_map;
        vector< vector<CV_Point> > area_list;

        //  方法
        double Dist(CV_Point a, CV_Point b);

        void BinSeg();
        int CalcRatio();
        void SkinArea();
        void Reducedlist();
        void SegmentDist();
        void StructVector();
    public:
        PornImageHandler();
        Mat& VisualSmap(Mat &visual_smap);
        vector<double> GetFeature(Mat& img_src);
};
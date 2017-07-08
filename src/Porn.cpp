//------------------------------------
//  A method to detect porn pictures
//  Author: mpsk
//  Beijing University of Technology
//  http://
//------------------------------------

#include <cmath>
#include "Porn.hpp"

//#define SHOW_INTER_RESULT

using namespace cv;
using namespace std;

double PornImageHandler::Dist(CV_Point a, CV_Point b)
{
    double dist;
    dist = sqrt((a.x - b.x)^2 + (a.y - b.y)^2);
    return dist;
}
        
void PornImageHandler::BinSeg()
{
    cvtColor(this->img, this->hsvimg, CV_BGR2HSV);  
    inRange(this->hsvimg, 
            Scalar(0, 57, 10), 
            Scalar(24, 174, 255), 
            this->s_map);
}
int PornImageHandler::CalcRatio()
{
    int count = 0;
    MatIterator_<Vec3b> it, end;
    for(it = this->s_map.begin<Vec3b>(), 
        end = this->s_map.end<Vec3b>(); 
        it != end; 
        it++)
    {
        if((*it)[0]==255 && (*it)[1]==255 && (*it)[2] == 255)
        {
            count++;
        }
    }
    return count;
}
void PornImageHandler::SkinArea()
{
    int nCols = this->s_map.cols;
    int nRows = this->s_map.rows;
    Mat s_map_gray, area_label;
    //  该死的Mat::zeros()以后只使用Mat::create()
    area_label.create(nRows, nCols, CV_8U);
    //  这里的二值图像是单通道的
    this->s_map.copyTo(s_map_gray);
    int count = 0, area = 1;
    vector<CV_Point> pixels;
    queue<CV_Point> seeds;
    for(int j=0; j<nRows; ++j)
    {
        for(int i=0; i<nCols; ++i)
        {
            //  map里面没有标签
            uchar *map_ptr = s_map_gray.ptr<uchar>(j);
            uchar *label_ptr = area_label.ptr<uchar>(j);
            if(label_ptr[i]==0 && map_ptr[i]==255)
            {
                seeds.push(CV_Point(i,j));
                if(!pixels.empty())
                {
                    area_list.push_back(pixels);
                }
                area = 1;
                //cout << "area_found! No. " << ++count << endl;
                pixels.clear();
                pixels.push_back(CV_Point(i,j));
            }
            else
                continue;
            while(!seeds.empty())
            {
                CV_Point point = seeds.front();seeds.pop();
                //  需要注意如何使用相应的遍历相邻边缘的算法
                label_ptr = area_label.ptr<uchar>(j);
                label_ptr[i] = 1;
                for(int m=-1;m<2;m++)
                {
                    for(int n=-1;n<2;n++)
                    {
                        label_ptr = area_label.ptr<uchar>(point.y+m);
                        map_ptr = s_map_gray.ptr<uchar>(point.y+m);
                        if  ((point.y+m>=0 && point.y+m<s_map_gray.rows &&
                            point.x+n>=0 && point.x+n<s_map_gray.cols) &&
                            //  如果再s_map上显示是皮肤区域
                            (map_ptr[point.x+n]==255) &&
                            //  满足十字邻接条件的
                            (abs(m)<1 || abs(n)<1) &&
                            //  在area_label上没有被标记的
                            label_ptr[point.x+n]==0)
                        {
                            area++;
                            label_ptr[point.x+n] = 1;
                            pixels.push_back(CV_Point(point.x+n, point.y+m));
                            seeds.push(CV_Point(point.x+n, point.y+m));
                        }
                    }
                }
                
            }
        }
    }
}
void PornImageHandler::Reducedlist()
{

}
void PornImageHandler::SegmentDist()
{

}
void PornImageHandler::StructVector()
{

}

PornImageHandler::PornImageHandler()
{

}
Mat& PornImageHandler::VisualSmap(Mat &visual_smap)
{
    //  3-channel BGR
    int nCols = this->s_map.cols;
    int nRows = this->s_map.rows;
    int nChannels = 3;
    visual_smap.create(nRows, nCols, CV_8UC3);
    int label[3] = {0,0,0};
    vector< vector<CV_Point> >::iterator it_a = this->area_list.begin();
    //  ALL ZEROS
    for(int j=0; j<nRows; j++)
    {
        uchar *p = visual_smap.ptr<uchar>(j);
        for(int i=0; i<nCols*nChannels; i++)
        {
            p[i] = 0;
        }
    }
    while(it_a!=this->area_list.end())
    {
        vector<CV_Point>::iterator it_b = (*it_a).begin();
        label[0] = (label[0] - 31)%255;
        label[1] = (label[1] - 57)%255;
        label[2] = (label[2] - 97)%255;
        while(it_b!=(*it_a).end())
        {
            visual_smap.ptr<uchar>((*it_b).y)[(*it_b).x*nChannels] = label[0];
            visual_smap.ptr<uchar>((*it_b).y)[(*it_b).x*nChannels+1] = label[1];
            visual_smap.ptr<uchar>((*it_b).y)[(*it_b).x*nChannels+2] = label[2];
            it_b++;
        }
        it_a++;
    }
    return visual_smap;
}
vector<double> PornImageHandler::GetFeature(Mat& img_src)
{
    //  高斯模糊
    Mat img;
    Mat kernel = (Mat_<float>(3,3)<<    0.1,0.1,0.1,
                                        0.1,0.2,0.1,
                                        0.1,0.1,0.1);
    filter2D(img_src, img, img_src.depth(), kernel);
    vector<double> feature_vector;
    this->img = img;
    this->BinSeg();
    this->skin_ratio = (float)this->CalcRatio() / (this->s_map.rows * this->s_map.cols);
    this->SkinArea();
    img_src = this->VisualSmap(img_src);
    //this->Reducedlist();
    //this->SegmentDist();
    //this->StructVector();
#ifdef SHOW_INTER_RESULT
    imshow("HSV", this->hsvimg);
    imshow("Skin-Only", this->s_map);
    cout << "The Skin Ratio is " << this->skin_ratio * 100 << "%" << endl;
    vector< vector<CV_Point> >::iterator it_a = this->area_list.begin();
    cout << "The area_list is \n" << endl;
    while(it_a!=this->area_list.end())
    {
        vector<CV_Point>::iterator it_b = (*it_a).begin();
        while(it_b!=(*it_a).end())
        {
            cout << (*it_b).x << "-" << (*it_b).y << "\t";
            it_b++;
        }
        cout << "\n" << endl;
        it_a++;
    }
#endif
    return feature_vector;
}
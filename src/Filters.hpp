#pragma once
#include <iostream>
#include "opencv2/opencv.hpp"

using namespace cv;
using namespace std;

class Filters
{
    private:
        Mat Kernel;
    public:
        void Conv2D();
};

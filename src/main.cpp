#include "iostream"
#include "opencv2/opencv.hpp"

#include "Filters.hpp"

using namespace cv;
using namespace std;

int main(int argc, char **argv)
{
    if(argc == 1)
    {
        VideoCapture cap(0);
        if(!cap.isOpened())
        {
            cout << "Cam Error!" << endl;
            return -1;
        }
        Mat frame;
        while(true)
        {
            if(cap.read(frame))
            {
                imshow("Vid", frame);
                //imshow("Result", frame);
            }
            else
            {
                cout << "can't read from cam" << endl;
            }
            if(waitKey(30) == 27)
            {
                cout << "Exited"<< endl;
                break;
            }
        }
    }
    else if(argc == 2)
    {
        Mat image;
        image = imread( argv[1], 1 );
        CV_Assert(image.depth() == CV_8U);
        if (!image.data)
        {
            cout << "No image data \n" << endl;
            return -1;
        }
        namedWindow("Display Image", WINDOW_AUTOSIZE);
        imshow("Display Image", image);
        cout << "image loaded!" << endl;
        
        imshow("Result", image);
        waitKey(0);
    }
    else
    {
        cout << "argument error!" << endl;
    }
    return 0;
}
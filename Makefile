NAME = detect.out

SRC_PATH = src/
BIN_PATH = bin/

CC = gcc
CXX = g++ -Wall
CXXFLAGS = -std=c++11

SRC = ${wildcard $(SRC_PATH)*.cpp}
OBJ = ${patsubst %.cpp, %.o, $(SRC)}
LIBS = -lopencv_core
ALL_LIBS_CV2 = `pkg-config --libs opencv`
LDFLAGS_CV2 = -L/usr/local/opt/opencv/lib
INCFLAGS_CV2 = -I/usr/local/opt/opencv/include
LDFLAGS_CV3 = -L/usr/local/opt/opencv3/lib
INCFLAGS_CV3 = -I/usr/local/opt/opencv3/includes

all:$(OBJ)
	$(CXX) $(CXXFLAGS) -o $(BIN_PATH)$(NAME) $(OBJ) $(LDFLAGS_CV2) $(ALL_LIBS_CV2)

$(OBJ):%.o:%.cpp
	$(CXX) $(CXXFLAGS) $(INCFLAGS_CV2) -o $@ -c $<

.PHONY : clean
clean:
	rm -rf $(SRC_PATH)*.o

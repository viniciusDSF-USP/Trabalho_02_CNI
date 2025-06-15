all: main.o
	g++ src/main.o -o src/main `pkg-config --libs opencv4`
	./src/main

main.o: main.cpp
	g++ -c main.cpp -o src/main.o `pkg-config --cflags opencv4 eigen3`
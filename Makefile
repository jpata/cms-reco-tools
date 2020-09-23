validate: validate.C validate_main.cpp
	g++ -o validate validate.C validate_main.cpp `root-config --libs --cflags --ldflags`

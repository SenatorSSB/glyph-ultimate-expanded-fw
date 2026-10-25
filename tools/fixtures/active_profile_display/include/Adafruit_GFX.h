#pragma once
#include <string>
class Adafruit_GFX {
public:
 int x=0,y=0;
 std::string profile_text;
 void setCursor(int a,int b) {x=a;y=b;}
 void print(const char *s) {if(x==0&&y==0)profile_text=s;}
 int width() const {return 128;}
 void fillCircle(int,int,int,int) {}
 void drawCircle(int,int,int,int) {}
};

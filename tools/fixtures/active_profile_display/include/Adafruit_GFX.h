#pragma once
#include <cstdint>
#include <string>
#define PROGMEM
struct GFXglyph { uint16_t offset; uint8_t w,h,advance; int8_t x,y; };
struct GFXfont { uint8_t *bitmap; GFXglyph *glyph; uint16_t first,last; uint8_t advance; };
class Adafruit_GFX {
public:
 int x=0,y=0;
 std::string profile_text, dashboard_text, plate_text;
 void setCursor(int a,int b) {x=a;y=b;}
 void print(const char *s) {
  if(x==0&&y==0)profile_text=s;
  if(x==12&&y==20)dashboard_text=s;
  if(x==12&&y==30)plate_text=s;
 }
 void print(int) {}
 int width() const {return 128;}
 void fillCircle(int,int,int,int) {}
 void drawCircle(int,int,int,int) {}
 void drawBitmap(int,int,const unsigned char *,int,int,int) {}
 void fillRect(int,int,int,int,int) {}
 void setFont(const GFXfont *) {}
 void setTextSize(int) {}
};

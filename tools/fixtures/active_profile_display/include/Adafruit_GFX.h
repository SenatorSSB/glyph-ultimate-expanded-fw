#pragma once
#include <cstdint>
#include <string>
#include <array>
#define PROGMEM
#define pgm_read_byte(p) (*(p))
struct GFXglyph { uint16_t offset; uint8_t w,h,xAdvance; int8_t x,y; };
struct GFXfont { uint8_t *bitmap; GFXglyph *glyph; uint16_t first,last; uint8_t advance; };
class Adafruit_GFX {
public:
 int x=0,y=0;
 int dashboard_max_x=-1;
 std::array<bool,128*64> dashboard_pixels{};
 const GFXfont *font=nullptr;
 const GFXfont *dashboard_font=nullptr;
 std::string profile_text, dashboard_text, plate_text;
 void setCursor(int a,int b) {x=a;y=b;if(x==12&&y==20){dashboard_text.clear();dashboard_max_x=-1;dashboard_pixels.fill(false);}}
 void print(const char *s) {
  if(x==0&&y==0)profile_text=s;
  if(x==12&&y==20)dashboard_text=s;
  if(x==12&&y==30)plate_text=s;
 }
 void print(int) {}
 // Equivalent to the production custom-font drawChar bit walk for size 1.
 size_t write(uint8_t c) {
  if (!font || c<font->first || c>font->last) return 1;
  auto g=font->glyph[c-font->first];
  if(y==20) {
   dashboard_text.push_back(static_cast<char>(c));
   unsigned bit=0;
   for(unsigned row=0;row<g.h;++row) for(unsigned col=0;col<g.w;++col,++bit)
    if(font->bitmap[g.offset+bit/8] & (0x80 >> (bit%8))) {
     int px=x+g.x+col;
     int py=y+g.y+row;
     if(px>=0 && px<128 && py>=0 && py<64) dashboard_pixels[py*128+px]=true;
     if(px>dashboard_max_x) dashboard_max_x=px;
    }
  }
  x+=g.xAdvance;
  return 1;
 }
 int width() const {return 128;}
 void fillCircle(int,int,int,int) {}
 void drawCircle(int,int,int,int) {}
 void drawBitmap(int,int,const unsigned char *,int,int,int) {}
 void fillRect(int,int,int,int,int) {}
 void setFont(const GFXfont *f) {font=f;if(f && !dashboard_font)dashboard_font=f;}
 void setTextSize(int) {}
};

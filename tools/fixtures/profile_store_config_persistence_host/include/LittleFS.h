#pragma once
#include <Arduino.h>
#include <map>
#include <string>
#include <functional>
struct LittleFSConfig { explicit LittleFSConfig(bool value=true):auto_format(value){} bool auto_format; };
struct HostFS;
class File final: public Stream {
 public:
  std::shared_ptr<std::vector<uint8_t>> bytes; HostFS *fs=nullptr; std::string name; size_t pos=0;
  explicit operator bool()const{return bool(bytes);}
  size_t size()const{return bytes?bytes->size():0;}
  int available()override{return bytes?int(bytes->size()-pos):0;}
  int read()override;
  int read(uint8_t *data,size_t n){return int(readBytes(data,n));}
  int peek()override{return bytes&&pos<bytes->size()?(*bytes)[pos]:-1;}
  void flush()override{}
  bool seek(size_t n){if(!bytes||n>bytes->size())return false;pos=n;return true;}
  size_t position()const{return pos;}
  size_t write(uint8_t b)override{return write(&b,1);}
  size_t write(const uint8_t *data,size_t n)override;
  void close(){}
};
struct HostFS {
 using Bytes=std::vector<uint8_t>;std::map<std::string,std::shared_ptr<Bytes>> files;
 std::string fault;unsigned mutations=0;bool published=false;unsigned write_calls=0,fail_write_call=0;
 bool setConfig(const LittleFSConfig &c){return !c.auto_format;}
 bool begin(){return true;}void end(){}
 bool exists(const char *p){return files.count(p);}
 bool remove(const char *p){++mutations;if(fault==std::string("remove:")+p)return false;return files.erase(p)!=0;}
 bool rename(const char *a,const char *b){
  ++mutations;if(fault==std::string("rename:")+a)return false;
  auto it=files.find(a);if(it==files.end()||files.count(b))return false;
  files[b]=it->second;files.erase(it);if(std::string(a)=="config-v2.tmp")published=true;return true;
 }
 File open(const char *p,const char *mode){
  if(fault==std::string("open:")+p || (published&&fault=="postpublish-open"))return {};
  if(mode[0]=='w'){++mutations;files[p]=std::make_shared<Bytes>();}
  if(!files.count(p))return {};
  File f;f.bytes=files[p];f.fs=this;f.name=p;return f;
 }
 void reset(){files.clear();fault.clear();mutations=0;published=false;write_calls=fail_write_call=0;}
};
inline HostFS &hostfs(){static HostFS fs;return fs;}
#define LittleFS (hostfs())
inline int File::read(){if(!bytes||pos>=bytes->size()||fs->fault=="read:"+name)return -1;return (*bytes)[pos++];}
inline size_t File::write(const uint8_t *data,size_t n){if(!bytes||fs->fault=="write:"+name||++fs->write_calls==fs->fail_write_call)return 0;if(pos+n>bytes->size())bytes->resize(pos+n);std::memcpy(bytes->data()+pos,data,n);pos+=n;return n;}

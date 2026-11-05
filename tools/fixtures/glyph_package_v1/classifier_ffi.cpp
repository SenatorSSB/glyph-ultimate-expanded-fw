#include "core/PackageNamespaceClassifier.hpp"
#include <cstring>
namespace p=package_storage;
struct Callbacks {
 int(*mounted)();int(*object)(size_t,char*,size_t*,int*);int(*extent)(const char*,size_t*);int(*read)(const char*,size_t,unsigned char*,size_t);
 int(*config)(const char*,unsigned,p::ConfigFacts*);int(*row)(const char*,size_t,p::RowFacts*);int(*rgb)(const char*,size_t,unsigned char*);
 int(*native)(const char*,size_t,const unsigned char*,size_t);int(*legacy)(const unsigned char*,size_t);int(*append)(const char*,const char*);
};
struct Reader:p::NamespaceReader{
 Callbacks &c;bool failed=false;explicit Reader(Callbacks&x):c(x){}
 bool MountedAndConfigured()const override{return c.mounted();}
 bool ObservationFailed()const override{return failed;}
 bool ObjectAt(size_t i,p::NamespaceObject&o,bool&eof)override{int e=0;bool ok=c.object(i,o.path,&o.bytes,&e);eof=e;o.directory=false;if(!ok)failed=true;return ok;}
 p::Probe Extent(const char*p,size_t&n)override{const int result=c.extent(p,&n);if(result==2)failed=true;return static_cast<p::Probe>(result);}
 bool Read(const char*p,size_t o,unsigned char*b,size_t n)override{const bool ok=c.read(p,o,b,n);if(!ok)failed=true;return ok;}
 bool Config(const char*p,unsigned m,p::ConfigFacts&f)override{return c.config(p,m,&f);}
 bool Row(const char*p,size_t i,p::RowFacts&f)override{return c.row(p,i,&f);}
 bool Rgb(const char*p,size_t i,unsigned char*h)override{return c.rgb(p,i,h);}
 bool Native(const char*p,size_t i,const unsigned char*b,size_t n)override{return c.native(p,i,b,n);}
 bool LegacyProfile(const unsigned char*b,size_t n)override{return c.legacy(b,n);}
 bool AppendConfig(const char*b,const char*a)override{return c.append(b,a);}
};
extern "C" const char* classify(Callbacks*c,int*out){
 static p::ClassificationWorkspace w;static unsigned char a[3908],b[3908],ctrl[3924],intent[512],record[4128];
 Reader reader(*c);auto result=p::ClassifyNamespace(reader,{w,a,b,ctrl,intent,record});out[0]=int(result.logical);out[1]=result.write_fenced;out[2]=int(result.floor);return result.diagnostic;
}
extern "C" size_t workspace_size(){return sizeof(p::ClassificationWorkspace);}
extern "C" size_t facts_size(){return sizeof(p::ConfigFacts);}

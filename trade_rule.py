# -*- coding: utf-8 -*-
dire='./trade_rule'
mode=(1,0)
gtype=1

def __change_self(dir,mod,gtyp,file,sig=0):
    f=open(file,'r',encoding='utf-8')
    data=f.readlines()
    f.close()
    if data[1][:4]=='dire': #"dire='./trade_rule/'\n"
        if data[2][:4]=='mode':
            if data[3][:4]=='gtyp':
                new=f"gtype={gtyp}\n"
                if data[3]!=new:
                    data[3]=new
                    if not sig:
                        sig=1
                new=f"mode={mod}\n"
                if data[2]!=new:
                    data[2]=new
                    if not sig:
                        sig=1
                new=f"dire='{dir}'\n"
                if data[1]!=new:
                    data[1]=new
                    if not sig:
                        sig=1
            else:
                sig=2
        else:
            sig=2
    else:
        sig=2
    if sig==2:
        data.insert(1,f"gtype={gtyp}\n")
        data.insert(1,f"mode={mod}\n")
        data.insert(1,f"dire='{dir}'\n")
    if sig:
        f=open(file,'w',encoding='utf-8')
        f.writelines(data)
        f.close()

def __change_dire(old,new):
    import shutil
    shutil.move(old,new)

def __load(name,load,lz=None):
    f=open(name,'rb')
    if lz is not None:
        lzd=lz.decompress
        data=load(lzd(f.read()))
    else:
        data=load(f)
    f.close()
    return data

def __dump(name,data,dump):
    f=open(name,'wb')
    dump(data,f)
    f.close()

def main(mod:tuple[int,int],gtyp:int=None,ori='trade_rule/',
         pre0={
             (1,0):'stock_all',(1,1):'stock_rule',(1,2):'stock_info',(1,3):'stock_dates',
             (2,0):'future_all',(2,1):'future_rule',(2,2):'future_info',(2,3):'future_dates',
             (3,0):'all',(3,1):'all_rule',(3,2):'all_info',(3,3):'all_dates'
         },
         pre1={
             (1,0):'stock_all.xz',(1,1):'stock_rule.xz',(1,2):'stock_info.xz',(1,3):'stock_dates.xz',
             (2,0):'future_all.xz',(2,1):'future_rule.xz',(2,2):'future_info.xz',(2,3):'future_dates.xz',
             (3,0):'all.xz',(3,1):'all_rule.xz',(3,2):'all_info.xz',(3,3):'all_dates.xz'
         },
        ):
    '''使用本函数来获取关于交易字段、交易规则、交易时间规定等信息
    mod:获取数据类型
        =(1,0):获取股票、期权的名称规则、信息规则、时间规则
        =(1,1):获取股票、期权的名称规则
        =(1,2):获取股票、期权的信息规则
        =(1,3):获取股票、期权的时间规则
        =(2,0):获取期货的名称规则、信息规则、时间规则
        =(2,1):获取期货的名称规则
        =(2,2):获取期货的信息规则
        =(2,3):获取期货的时间规则
        =(3,0):获取股票、期权、期货的名称规则、信息规则、时间规则
        =(3,1):获取股票、期权、期货的名称规则
        =(3,2):获取股票、期权、期货的信息规则
        =(3,3):获取股票、期权、期货的时间规则
    gtyp:获取方式
        =0:无压缩方式，获取后就直接读取
        =1:压缩方式，第一次获取后会进行解压缩，之后只要解压后文件还存在就不会解压
    return:
        单个具体的数据类型时为字典，多个时为字典按顺序组成的元组
    '''
    #仅在函数内进行所有操作，避免对函数外部造成任何影响
    '''
    #本文件不会移动自身文件位置，只会主动移动数据文件、数据文件夹位置到工作路径去#
    首先检查需要的文件是否在路径内：
        在工作路径：
            在就直接加载返回数据，返回前判断本文件中提示参数（三个）是否需要更改（按优先级去更改、移动文件夹与文件）
        不在且为压缩方式获取的：
            尝试去解压缩文件到工作路径，成功则返回数据，返回前判断本文件中提示参数（三个）是否需要更改（按优先级去更改、移动文件夹与文件）
        还未成功就转移到本文件中提示路径：
            在就直接加载返回数据，返回前移动数据文件夹到工作路径去，并判断本文件中提示参数（三个）是否需要更改（按优先级去更改、移动文件夹与文件）
        还未找到且为压缩方式获取的：
            尝试去解压缩文件到工作路径，成功则返回数据，返回前判断本文件中提示参数（三个）是否需要更改（按优先级去更改、移动文件夹与文件）
        还未成功就转移到本文件所在路径：
            在就直接加载返回数据，返回前移动数据文件夹到工作路径去，并判断本文件中提示参数（三个）是否需要更改（按优先级去更改、移动文件夹与文件）
        还未找到且为压缩方式获取的：
            尝试去解压缩文件到工作路径，成功则返回数据，返回前判断本文件中提示参数（三个）是否需要更改（按优先级去更改、移动文件夹与文件）
        还未成功就从指定网址去按获取方式下载（如果需要解压缩就会解压）到工作路径中去，之后返回数据，返回前判断本文件中提示参数是否需要更改（按优先级去更改、移动文件夹与文件）
    '''
    import os,pickle,datetime #datetime给数据中的时间数据提供实例化支持
    exists=os.path.exists
    workdir=os.getcwd().replace('\\','/')+'/' #'D:\\projects\\trade_daytype'
    self=os.path.abspath(__file__).replace('\\','/') #'D:\\projects\\trade_daytype\\trade_rule.py'
    selfdir=self[:self.rfind('/')+1]
    objdir=workdir+ori
    if exists(objdir): #先检查工作路径下是否有该数据文件夹
        if exists(objdir+pre0[mod]): #数据文件夹中是否有数据文件
            __change_self(objdir,mod,gtyp,self)
            return __load(objdir+pre0[mod],pickle.load)
        elif gtyp==1 and exists(objdir+pre1[mod]):
            import lzma
            data=__load(objdir+pre1[mod],pickle.loads,lzma.LZMADecompressor(format=lzma.FORMAT_XZ).decompress)
            __dump(objdir+pre0[mod],data,pickle.dump)
            __change_self(objdir,mod,gtyp,self)
            return data
    if exists(workdir+pre0[mod]): #工作路径下是否有数据文件呢
        os.makedirs(objdir,exist_ok=True)
        __change_dire(workdir+pre0[mod],objdir)
        __change_self(objdir,mod,gtyp,self)
        return __load(objdir+pre0[mod],pickle.load)
    elif gtyp==1 and exists(workdir+pre1[mod]):
        import lzma
        data=__load(workdir+pre1[mod],pickle.loads,lzma.LZMADecompressor(format=lzma.FORMAT_XZ).decompress)
        os.makedirs(objdir,exist_ok=True)
        __dump(objdir+pre0[mod],data,pickle.dump)
        __change_self(objdir,mod,gtyp,self)
        return data
    #等于的时候不用再去判断了
    if dire!=objdir and exists(dire): #默认路径下是否有数据文件夹呢（如果默认路径与工作路径不一致的话）
        if exists(dire+pre0[mod]):
            __change_dire(dire,workdir) #是要放到工作路径中，从而把数据的路径变成objdir
            __change_self(objdir,mod,gtyp,self)
            return __load(objdir+pre0[mod],pickle.load)
        elif gtyp==1 and exists(dire+pre1[mod]):
            import lzma
            data=__load(dire+pre1[mod],pickle.loads,lzma.LZMADecompressor(format=lzma.FORMAT_XZ).decompress)
            os.makedirs(objdir,exist_ok=True)
            __dump(objdir+pre0[mod],data,pickle.dump)
            __change_self(objdir,mod,gtyp,self)
            return data
    if selfdir!=objdir and selfdir!=dire and exists(selfdir):
        if exists(selfdir+pre0[mod]):
            __change_dire(selfdir,workdir) #是要放到工作路径中，从而把数据的路径变成objdir
            __change_self(objdir,mod,gtyp,self)
            return __load(objdir+pre0[mod],pickle.load)
        elif gtyp==1 and exists(selfdir+pre1[mod]):
            import lzma
            data=__load(selfdir+pre1[mod],pickle.loads,lzma.LZMADecompressor(format=lzma.FORMAT_XZ).decompress)
            os.makedirs(objdir,exist_ok=True)
            __dump(objdir+pre0[mod],data,pickle.dump)
            __change_self(objdir,mod,gtyp,self)
            return data
    print(f'{datetime.datetime.now()} 模块-trade_rule-正从指定连接获取给定数据')
    os.makedirs(objdir,exist_ok=True)
    if not gtyp:
        import requests,base64
        retu=requests.get(f'https://api.github.com/repos/sheen-reba/trade_daytype/contents/{pre0[mod]}?ref=main')
        if retu.status_code==200:
            data=base64.b64decode(retu.json()['content'])
            f=open(objdir+pre0[mod],'wb')
            f.write(data)
            f.close()
            __change_self(objdir,mod,gtyp,self)
            return pickle.loads(data)
    elif gtyp==1:
        print(f'{datetime.datetime.now()} 模块-trade_rule-正从指定连接获取给定数据')
        import requests,lzma,base64
        retu=requests.get(f'https://api.github.com/repos/sheen-reba/trade_daytype/contents/{pre1[mod]}?ref=main')
        if retu.status_code==200:
            xz=base64.b64decode(retu.json()['content'])
            f=open(objdir+pre1[mod],'wb')
            f.write(xz)
            f.close()
            data=pickle.loads(lzma.LZMADecompressor(format=lzma.FORMAT_XZ).decompress(xz))
            os.makedirs(objdir,exist_ok=True)
            __dump(objdir+pre0[mod],data,pickle.dump)
            __change_self(objdir,mod,gtyp,self)
            return data
    print(f'{datetime.datetime.now()} 模块-trade_rule-从指定连接获取给定数据失败，连接状态码为{retu.status_code}')

if __name__=='__main__':
    main((3,0),1)
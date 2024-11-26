# -*- coding: utf-8 -*-
dire='./trade_daytype'
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

def __decrypt(name,loads,decode,lz=None):
    f=open(name,'rb')
    if lz is not None:
        lzd=lz.decompress
        data=loads(decode(lzd(f.read())))
    else:
        data=loads(decode(f.read()))
    f.close()
    return data

def __result(name,load):
    f=open(name,'rb')
    data=load(f)
    f.close()
    return data

def main(mod:tuple[int,int],gtyp:int=None,ori='trade_rule',
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
    import os,pickle
    exists=os.path.exists
    work=os.getcwd().replace('\\','/') #'D:\\projects\\trade_daytype'
    path=os.path.abspath(__file__).replace('\\','/') #'D:\\projects\\trade_daytype\\trade_rule.py'
    objpath=work+'/'+ori
    if exists(objpath):
        if exists(objpath+'/'+pre0[mod]):
            return __result(objpath+'/'+pre0[mod],pickle.load)
        elif gtyp==1 and exists(objpath+'/'+pre1[mod]):
            __decrypt()
        __change_self(dir,mod,gtyp,file,sig=0)
    __change_self(work,2,2,path)
    if mod!=mode:
        ...
    import datetime,pickle,base64,lzma,requests
    a=requests.get('https://api.github.com/repos/sheen-reba/trade_daytype/contents/api.py?ref=main')
    b=a.json()
    # c=b64decode(b['content']).decode('utf-8')
    # exec(c)

if __name__=='__main__':
    main()
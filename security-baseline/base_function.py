import os
import shutil
from do_shell import run_shell

from prettytable import PrettyTable

def split_file_by_line(file,sym,condi,condi_order,out_order): #(`awk -F ":" '( $2 == "" ) { print $1 }' /etc/shadow`)
    #按行检索文档，并以sym作为分割，返回第order个分割结果等于condi的所有结果
    result=[]
    with open(file,'r') as f:
        lines=f.readlines()
        for l in lines:
            ls=l.split(sym)
            #print(ls)
            if ls[condi_order]==condi:
                result.append(ls[out_order])
    return result

def grep_find(para,file): #寻找指定的行
    command='grep "'+para+'" '+file
    return run_shell(command,False)

def sed_repalce(raw,new,file): #用new替换掉raw行
    command='sed -i "s#'+raw+'#'+new+'#g" '+file
    run_shell(command,False)

def append_line(new_line,file): #向文件添加一行
    command='echo "'+new_line+'" >>'+file
    run_shell(command)

def remove_line(line,file): #删除文件中有特定内容中的行
    command='sed -i "/'+line+'/d" '+file
    run_shell(command)

def cp_file(raw_path,new_path,show=True):
    command=r'cp -a '+raw_path+' '+new_path
    run_shell(command,show)

def rm_file(raw_path,show=True):
    command = r'rm -f ' + raw_path
    run_shell(command,show)


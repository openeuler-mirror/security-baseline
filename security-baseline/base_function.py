import os
import shutil
from do_shell import run_shell
from config import fixed_config
from prettytable import PrettyTable
config=fixed_config()
Initial_dir=config.Initial_dir

class BaseFix():
    def __init__(self):
        self.id=''
        self.path=''
        self.description = ''

    def run(self):
        pass

    def backup(self,show=True):  # 对操作文件进行备份
        if self.path!='' and os.path.exists(self.path):
            backup_file(Initial_dir, self.path)
            if show:
                print('加固项',self.id,'操作文件已备份。')
        else:
            if show:
                print('加固项',self.id,'无需备份！')

    def reset(self):
        if self.path=='' or reset_file(Initial_dir, self.path):
            pass
        else:
            self.recovery()

    def recovery(self):
        pass

    def check(self):
        pass


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

def backup_file(Initial_dir,file):
    if not os.path.exists(Initial_dir):
        os.mkdir(Initial_dir)
    if not os.path.exists(os.path.join(Initial_dir, file.split('/')[-1] + '_initialbak')) and os.path.exists(file):
        cp_file(file, os.path.join(Initial_dir, file.split('/')[-1] + '_initialbak'))

def reset_file(Initial_dir,file):
    if os.path.exists(os.path.join(Initial_dir, file.split('/')[-1] + '_initialbak')):
        cp_file(os.path.join(Initial_dir, file.split('/')[-1] + '_initialbak'),file)
        return True
    return False


def print_config(config):
    descriptions={'fix':u'执行加固','check':u'加固检测','repair':u' 还原加固内容 ','backup_path':u'备份目录'}
    table = PrettyTable(['config', 'set','description'])
    for c in vars(config):
        value=getattr(config, c)
        if type(value)==type([]):
            description=u'操作内容，空表示所有'
            table.add_row([c, value, description])
        else:
            if c in descriptions.keys():
                table.add_row([c, value,descriptions[c]])
            else:
                try:
                    table.add_row([c, value, descriptions[value]])
                except:
                    table.add_row([c, value, ''])
    print_line()
    print("设置项描述")
    print(table)

def print_desc(fixed_items):
    table = PrettyTable(['id', 'item', 'description'])
    for id in fixed_items.keys():
        table.add_row([id,fixed_items[id][1],fixed_items[id][0].description])
    print_line()
    print("加固项描述")
    print(table)
    print_line()

def print_line(sym=True):
    if sym:
        print('=====================================================================')
    else:
        print('---------------------------------------------------------------------')


def cprint(string,color):
    if color=='red':
        print("\033[31;1m"+string+"\033[0m")
    if color=='yellow':
        print("\033[33;1m"+string+"\033[0m")
    if color=='blue':
        print("\033[34;1m"+string+"\033[0m")
    if color=='green':
        print("\033[36;1m"+string+"\033[0m")
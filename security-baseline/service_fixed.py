# 账户加固相关项，编号从1开始

#path
import os.path
from do_shell import run_shell
from base_function import split_file_by_line,grep_find,sed_repalce,append_line,remove_line
from base_function import cp_file,rm_file,backup_file,reset_file,BaseFix
from base_function import comment_out_line,replace_line
from config import fixed_config

config=fixed_config()
Initial_dir=config.Initial_dir



class CHECK_EMPTY_PASS(BaseFix):
    def __init__(self):
        super().__init__()
        self.id=1
        self.config=fixed_config()
        self.path='/etc/shadow'
        self.description='空口令账户检查'

    def run(self): #空口令账户检查
        New_Pass = self.config.UserPass #'"1230"'
        Empty_Users=split_file_by_line(self.path,":","",1,0)   #Empty_User=(`awk -F ":" '( $2 == "" ) { print $1 }' /etc/shadow`)
        for Empty_User in Empty_Users:
            command='echo '+New_Pass+' | passwd --stdin '+Empty_User
            run_shell(command,False)

    def reset(self):
        reset_file(Initial_dir,self.path)

    def check(self):
        Empty_Users = split_file_by_line(self.path, ":", "", 1, 0)
        flag=True
        if Empty_Users!=[]:
            flag=False
            for Empty_User in Empty_Users:
                print('存在密码为空账户: ',Empty_User)
        return flag

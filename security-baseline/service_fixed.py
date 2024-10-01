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


class LOCKING_INVAILD_USER(BaseFix): #锁定无效账号
    def __init__(self):
        super().__init__()
        self.id = 2
        self.config = fixed_config()
        self.description='无效账户锁定'

    def run(self):
        Lock_users = self.config.Lock_users
        for Lock_user in Lock_users:
            command = 'id ' + Lock_user + ' 2>/dev/null | wc -l'
            num = run_shell(command,False)[0]
            if num == '1' or num == 1:
                
                command = 'passwd -l ' + Lock_user + ' &>/dev/null'
                run_shell(command,False)

    def recovery(self):  #对锁定的账户予以解封
        Lock_users = self.config.Lock_users
        for Lock_user in Lock_users:
            command = 'id ' + Lock_user + ' 2>/dev/null | wc -l'
            num = run_shell(command,False)[0]
            if num == '1' or num == 1:
                command = 'passwd -u ' + Lock_user + ' &>/dev/null'
                run_shell(command,False)

    def check(self):
        Lock_users = self.config.Lock_users
        flag=True
        for Lock_user in Lock_users:
            command = 'passwd -S ' + Lock_user + ' 2>/dev/null'
            num = run_shell(command,False)

            if num != []:
                num=num[0].split(' ')[1]
                if num!='LK':
                    return False
        return flag


class CHECK_UID_ZERO(BaseFix): #检测UID权限为0的账户，并删除
    def __init__(self):
        super().__init__()
        self.id = 3
        self.path='/etc/passwd'
        self.description='UID权限为0的非root账户处置'

    def run(self):
        UidZeroUser =split_file_by_line('/etc/passwd',":",'0',2,0)

        if len(UidZeroUser)!=1 and UidZeroUser!=['root']:
            for ZeroUser in UidZeroUser:
                if ZeroUser != 'root':
                    command='userdel -fr '+ZeroUser +' 2>/dev/null'
                    run_shell(command,False)

    def reset(self):
        if reset_file(Initial_dir, self.path):
            pass
        else:
            self.recovery()

    def check(self):
        UidZeroUser = split_file_by_line('/etc/passwd', ":", '0', 2, 0)
        flag=True
        if len(UidZeroUser) != 1 and UidZeroUser != ['root']:
            flag=False
            for ZeroUser in UidZeroUser:
                if ZeroUser != 'root':
                    print('存在非root账户管理员: ',ZeroUser)
        return flag


class REBUILD_FILE(BaseFix): #修改密码相关限制，1.密码最长有效天数，2.密码最小长度，3.密码最短有效期，4.密码有效期结束前七天提醒修改
    def __init__(self):
        super().__init__()
        self.id = 4
        self.path='/etc/login.defs'
        self.description='用户密码长度和有效期相关设定'

    def run(self):
        if grep_find('^PASS_MAX_DAYS', self.path)!=[]:
            sed_repalce(grep_find('^PASS_MAX_DAYS', self.path)[0], 'PASS_MAX_DAYS	90', self.path)
        else:
            append_line('PASS_MAX_DAYS	90', self.path)
        if grep_find('^PASS_MIN_LEN', self.path)!=[]:
            sed_repalce(grep_find('^PASS_MIN_LEN', self.path)[0], 'PASS_MIN_LEN	   8', self.path)
        else:
            append_line('PASS_MIN_LEN	   8', self.path)
        if grep_find('^PASS_MIN_DAYS', self.path)!=[]:
            sed_repalce(grep_find('^PASS_MIN_DAYS', self.path)[0], 'PASS_MIN_DAYS	1', self.path)
        else:
            append_line('PASS_MIN_DAYS	1',self.path)
        if grep_find('^PASS_WARN_AGE', self.path)!=[]:
            sed_repalce(grep_find('^PASS_WARN_AGE', self.path)[0], 'PASS_WARN_AGE	7', self.path)
        else:
            append_line('PASS_WARN_AGE	7',self.path)

    def reset(self):
        if reset_file(Initial_dir, self.path):
            pass
        else:
            self.recovery()

    def recovery(self):
        if grep_find('^PASS_MAX_DAYS', self.path)!=[]:
            sed_repalce(grep_find('^PASS_MAX_DAYS', self.path)[0], 'PASS_MAX_DAYS	99999', self.path)
        else:
            append_line('PASS_MAX_DAYS	99999', self.path)
        if grep_find('^PASS_MIN_LEN', self.path)!=[]:
            sed_repalce(grep_find('^PASS_MIN_LEN', self.path)[0], 'PASS_MIN_LEN	   8', self.path)
        else:
            append_line('PASS_MIN_LEN	   8', self.path)
        if grep_find('^PASS_MIN_DAYS', self.path)!=[]:
            sed_repalce(grep_find('^PASS_MIN_DAYS', self.path)[0], 'PASS_MIN_DAYS	0', self.path)
        else:
            append_line('PASS_MIN_DAYS	0',self.path)
        if grep_find('^PASS_WARN_AGE', self.path)!=[]:
            sed_repalce(grep_find('^PASS_WARN_AGE', self.path)[0], 'PASS_WARN_AGE	7', self.path)
        else:
            append_line('PASS_WARN_AGE	7',self.path)

    def check(self):
        flag=True
        try:
            PASS_MAX_DAYS=int(grep_find('^PASS_MAX_DAYS', self.path)[0].split('\t')[1])
        except:
            PASS_MAX_DAYS=99999
        try:
            PASS_MIN_LEN = int(grep_find('^PASS_MIN_LEN', self.path)[0].split('\t')[1])
        except:
            PASS_MIN_LEN=1
        try:
            PASS_MIN_DAYS = int(grep_find('^PASS_MIN_DAYS', self.path)[0].split('\t')[1])
        except:
            PASS_MIN_DAYS=0
        try:
            PASS_WARN_AGE = int(grep_find('^PASS_WARN_AGE', self.path)[0].split('\t')[1])
        except:
            PASS_WARN_AGE=7
        print('密码有效期：',PASS_MAX_DAYS)
        print('密码最短长度：', PASS_MIN_LEN)
        print('密码最短修改频率：',PASS_MIN_DAYS)
        print('密码过期提醒天数：', PASS_WARN_AGE)
        if [PASS_MAX_DAYS,PASS_MIN_LEN,PASS_MIN_DAYS,PASS_WARN_AGE]!=[90,8,1,7]:
            flag=False
        return flag


class SET_CRACK(BaseFix): #设置密码组成限制，difok新密码必须和旧密码3位不同，密码组成必须有大小写字母，数字，特殊符号
    def __init__(self):
        super().__init__()
        self.id = 5
        self.path="/etc/pam.d/system-auth"
        self.description='用户密码组成相关设定'

    def run(self):
        flag=grep_find('^password    requisite     pam_cracklib.so', self.path)
        if flag !=[]: #若检测到满足的行，直接替换后取值即可
            sed_repalce(flag[0], 'password    requisite     pam_cracklib.so difok=3 dcredit=-1 lcredit=-1 ucredit=-1 credit=-1', self.path) #核实credit
        else: #若检测不到，则添加需求的行
            append_line('password    requisite     pam_cracklib.so difok=3 dcredit=-1 lcredit=-1 ucredit=-1 credit=-1',self.path)

    def reset(self):
        if reset_file(Initial_dir, self.path):
            pass
        else:
            self.recovery()

    def check(self):
        flag=True
        if grep_find('^password    requisite     pam_cracklib.so difok=3 dcredit=-1 lcredit=-1 ucredit=-1 credit=-1', self.path)==[]:
            flag=False
        return flag


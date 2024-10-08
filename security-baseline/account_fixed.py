"""
 (c) 2024 - Copyright CTyunOS Inc

 Authors:
   wukaishun <wuksh@chinatelecom.cn>

"""
# 账户加固相关项,编号从1开始

#path
import os.path
from do_shell import run_shell
from base_function import split_file_by_line,grep_find,sed_repalce,append_line,remove_line
from base_function import cp_file,rm_file,backup_file,reset_file,BaseFix
from base_function import comment_out_line,replace_line,check_file_permission
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
            command='echo "'+Empty_User+':'+New_Pass+'" | chpasswd'
            run_shell(command,False)

    def reset(self,backup_path=Initial_dir):
        reset_file(backup_path,self.path)

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
        sed_repalce(grep_find('^INACTIVE', "/etc/default/useradd")[0], 'INACTIVE=0', "/etc/default/useradd")

    def recovery(self,backup_path=''):  #对锁定的账户予以解封
        Lock_users = self.config.Lock_users
        for Lock_user in Lock_users:
            command = 'id ' + Lock_user + ' 2>/dev/null | wc -l'
            num = run_shell(command,False)[0]
            if num == '1' or num == 1:
                command = 'passwd -u ' + Lock_user + ' &>/dev/null'
                run_shell(command,False)
        sed_repalce(grep_find('^INACTIVE', "/etc/default/useradd")[0], 'INACTIVE=-1', "/etc/default/useradd")

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
        flags=grep_find('^INACTIVE',"/etc/default/useradd")[0]
        if flags==[]:
            pass
        else:
            flags=flags.split("=")[-1]
        if flags!="0":
            return False
        return flag

class CHECK_UID_ZERO(BaseFix): #检测UID权限为0的账户,并删除
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
                    command='userdel -f '+ZeroUser +' 2>/dev/null'
                    run_shell(command,False)

    def reset(self,backup_path=Initial_dir):
        if reset_file(backup_path, self.path):
            pass
        else:
            self.recovery(backup_path=backup_path)
        UidZeroUser =split_file_by_line('/etc/passwd',":",'0',2,0)
        if UidZeroUser!=[]:
            for ZeroUser in UidZeroUser:
                if ZeroUser=="root":
                    continue
                if not os.path.exists(os.path.join("/home/",ZeroUser)):
                    os.mkdir(os.path.join("/home/",ZeroUser))
                    run_shell("chown -R "+ZeroUser+" "+os.path.join("/home/",ZeroUser))
                    run_shell("chmod 700 "+os.path.join("/home/",ZeroUser))

    def check(self):
        UidZeroUser = split_file_by_line('/etc/passwd', ":", '0', 2, 0)
        flag=True
        if len(UidZeroUser) != 1 and UidZeroUser != ['root']:
            flag=False
            for ZeroUser in UidZeroUser:
                if ZeroUser != 'root':
                    print('存在非root账户管理员: ',ZeroUser)
        return flag


class REBUILD_FILE(BaseFix): #修改密码相关限制,1.密码最长有效天数,2.密码最小长度,3.密码最短有效期,4.密码有效期结束前七天提醒修改
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

    def reset(self,backup_path=Initial_dir):
        if reset_file(backup_path, self.path):
            pass
        else:
            self.recovery()

    def recovery(self,backup_path=Initial_dir):
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
        if PASS_MAX_DAYS>90 or PASS_MIN_LEN<8 or PASS_MIN_DAYS>1 or PASS_WARN_AGE<7:
            flag=False
        return flag


class SET_CRACK(BaseFix): #设置密码组成限制,difok新密码必须和旧密码3位不同,密码组成必须有大小写字母,数字,特殊符号
    def __init__(self):
        super().__init__()
        self.id = 5
        self.path="/etc/pam.d/system-auth"
        self.description='用户密码组成相关设定'

    def run(self):
        flag=grep_find('^password    requisite     pam_pwquality.so', self.path)
        if flag !=[]: #若检测到满足的行,直接替换后取值即可
            sed_repalce(flag[0], 'password    requisite     pam_pwquality.so difok=3 dcredit=-1 lcredit=-1 ucredit=-1 ocredit=-1', self.path) #核实credit
        else: #若检测不到,则添加需求的行
            append_line('password    requisite     pam_pwquality.so difok=3 dcredit=-1 lcredit=-1 ucredit=-1 ocredit=-1',self.path)

    def reset(self,backup_path=Initial_dir):
        if reset_file(backup_path, self.path):
            pass
        else:
            self.recovery(backup_path=backup_path)

    def check(self):
        flag=True
        if grep_find('^password    requisite     pam_pwquality.so difok=3 dcredit=-1 lcredit=-1 ucredit=-1 ocredit=-1', self.path)==[]:
            flag=False
        return flag


class LOGIN_USER_FALSE(BaseFix): #设定密码输入的情况下锁定账户,输入错误3次后,root锁定5分钟,其他用户锁定3分钟
    def __init__(self):
        super().__init__()
        self.id = 6
        self.path = "/etc/pam.d/system-auth"
        self.line = 'auth        required      pam_faillock.so preauth audit deny=3  unlock_time=180 even_deny_root root_unlock_time=300'
        self.description='密码输入错误锁定账户的设定'

    def run(self):
        flag=grep_find('^auth        required      pam_faillock.so', self.path)
        if flag !=[]: #若检测到满足的行,直接替换后取值即可
            sed_repalce(flag[0], self.line, self.path) #核实credit
        else: #若检测不到,则添加需求的行
            append_line(self.line,self.path)

    def recovery(self,backup_path=Initial_dir):
        flag = grep_find('^auth        required      pam_faillock.so', self.path)
        if flag != []:  # 若检测到满足的行,直接替换后取值即可
            sed_repalce(flag[0],
                        'auth        required      pam_faillock.so preauth audit deny=6  unlock_time=180 even_deny_root root_unlock_time=300',
                        self.path)  # 核实credit
        else:  # 若检测不到,则添加需求的行
            append_line(
                'auth        required      pam_faillock.so preauth audit deny=6 unlock_time=180 even_deny_root root_unlock_time=300',
                self.path)

    def check(self):
        flag=True
        if grep_find('^auth        required      pam_faillock.so preauth audit deny=3  unlock_time=180 even_deny_root root_unlock_time=300', self.path)==[]:
            flag=False
        return flag


class REBUILD_UMASK(BaseFix): #设置umask 027,表示默认创建新文件权限为750,也就是rxwr-x---(所有者全部权限,属组读写,其它人无)
    def __init__(self):
        super().__init__()
        self.id = 7
        self.path="/etc/profile"
        self.description='umask设置用户文件权限'

    def run(self):
        flags = grep_find('^umask', self.path)
        if flags != []:
            for flag in flags:
                sed_repalce(flag,'umask 027', self.path)
        else:
            append_line('umask 027',self.path)
        run_shell('source '+self.path)  

    def recovery(self,backup_path=Initial_dir):
        flags = grep_find('^umask', self.path)
        if flags != []:
            for flag in flags:
                sed_repalce(flag, 'umask 022', self.path)
        else:
            append_line('umask 022', self.path)
        run_shell('source '+self.path)  

    def check(self):
        umasks= grep_find('^umask', self.path)
        flag=False
        if umasks!=[] and '027' in umasks[-1]:
            flag=True
        return flag


class CHECK_USER_FILE(BaseFix): #修改与账户信息相关的文件权限,防止被恶意复制篡改
    def __init__(self):
        super().__init__()
        self.id = 8
        self.description='重要用户信息文件权限'

    def run(self):
        commands=['chmod 600 /etc/shadow','chmod 644 /etc/group','chmod 644 /etc/passwd']
        for command in commands:
            run_shell(command)

    def recovery(self,backup_path=Initial_dir): #不设置修复项目
        commands = ['chmod 600 /etc/shadow', 'chmod 644 /etc/group', 'chmod 644 /etc/passwd']
        for command in commands:
            run_shell(command)

    def check(self):
        commands = ['/etc/shadow 600', '/etc/group 644', '/etc/passwd 644']
        for file_mode in commands:
            if not check_file_permission(file_path=file_mode.split(' ')[0],mode_code=file_mode.split(' ')[1]):
                return False
        return True


class CHECK_ROOTDIR(BaseFix): #检查rootdir相关权限
    def __init__(self):
        super().__init__()
        self.id = 9
        self.description='rootdir权限设定'

    def run(self):
        commands=['chown root:root /root','chmod 700 /root'] #修复/root目录的归属,设置/root目录权限到root可用
        for command in commands:
            run_shell(command)

    def recovery(self,backup_path=Initial_dir):
        commands = ['chown root:root /root', 'chmod 550 /root']
        for command in commands:
            run_shell(command)

    def check(self):
        self.run()
        return True


class LOGIN_TMOUT(BaseFix): #设置登录无操作中断会话时间
    def __init__(self):
        super().__init__()
        self.id = 10
        self.path='/etc/profile'
        self.description='用户会话无操作时长中断设定'

    def run(self):
        remove_line('^TMOUT',self.path) #删除TMOUT开头的行
        remove_line('^export TMOUT', self.path) #删除export TMOUT开头的行
        append_line("export TMOUT=300",self.path) #在尾部追加行
        run_shell('source '+self.path) #使修改生效

    def recovery(self,backup_path=Initial_dir):
        remove_line('^TMOUT', self.path)  # 删除TMOUT开头的行
        remove_line('^export TMOUT', self.path)  # 删除export TMOUT开头的行
        run_shell('source '+self.path) #生效修改

    def check(self,backup_path=Initial_dir):
        tmouts=grep_find('TMOUT=',self.path)
        flag=False
        for tmout in tmouts:
            if tmout[0]=='#':
                continue
            if '300' in tmout and '3000' not in tmout:
                flag=True
        return flag


class SYSLOG(BaseFix): # 配置系统日志到路径
    def __init__(self):
        super().__init__()
        self.id = 11
        self.path="/etc/rsyslog.conf"
        self.description='本地系统日志设定'

    def run(self):
    #remove_line('^*.err;kern.debug;daemon.notice',path)
    #remove_line('^cron.*', path)
    #remove_line("^authpriv.*",path)

    #append_line('*.err;kern.debug;daemon.notice;        /var/log/messages',path)
    #append_line('cron.*                                 /var/log/cron',path)
    #append_line('authpriv.*                             /var/log/secure',path)
        try:
            sed_repalce(grep_find('^*.err;kern.debug;daemon.notice', self.path)[0], '*.err;kern.debug;daemon.notice;        /var/log/messages', self.path)
        except:
            append_line('*.err;kern.debug;daemon.notice;        /var/log/messages', self.path)
        try:
            sed_repalce(grep_find('^cron.*', self.path)[0],'cron.*                                 /var/log/cron', self.path)
        except:
            append_line('cron.*                                 /var/log/cron', self.path)
        try:
            sed_repalce(grep_find('^authpriv.*', self.path)[0], 'authpriv.*                             /var/log/secure', self.path)
        except:
            append_line('authpriv.*                             /var/log/secure', self.path)
        run_shell('systemctl restart rsyslog')

    def recovery(self,backup_path=Initial_dir):
        comment_out_line(self.path,'*.err;kern.debug;daemon.notice',"#")
        comment_out_line(self.path,'cron.*',"#")
        comment_out_line(self.path,"authpriv.*","#")
        run_shell('systemctl restart rsyslog') #生效设置

    def check(self,backup_path=Initial_dir):
        log1=grep_find('^*.err;kern.debug;daemon.notice', self.path)
        log2=grep_find('^cron.*', self.path)
        log3=grep_find('^authpriv.*',self.path)
        if log1==[] or log2==[] or log3==[]:
            return False
        if log1!=[] and '/var/log/messages' not in log1[0]:
            return False
        if log2!=[] and '/var/log/cron' not in log2[0]:
            return False
        if log3!=[] and '/var/log/secure' not in log3[0]:
            return False
        return True


class RSYSLOG(BaseFix): #设置远程log的存放
    def __init__(self):
        super().__init__()
        self.id = 12
        self.path='/etc/rsyslog.conf'
        self.description='远程日志设定'

    def run(self):
        remove_line('@192.168.0.1',self.path)
        append_line("*.*    @192.168.0.1",self.path)
        run_shell('systemctl restart rsyslog')

    def recovery(self,backup_path=Initial_dir):
        remove_line('@192.168.0.1',self.path)
        run_shell('systemctl restart rsyslog')

    def check(self): #直接加固即可
        self.run()
        return True


class ADD_SECURE(BaseFix): #添加安全账户,用于系统安全管理
    def __init__(self):
        super().__init__()
        self.id = 13
        self.path='/etc/sudoers'
        self.config=fixed_config()
        self.description='添加用于安全管理的账户'

    def run(self):
        UserName=self.config.UserName
        UserPass=self.config.UserPass
        SecureNum=int(run_shell('id '+UserName+' 2>/dev/null|wc -l',False)[0])
        if SecureNum!=1:
            run_shell('useradd '+UserName)
            command = 'echo ' + UserPass + ' | passwd --stdin ' + UserName+ ' &>/dev/null'
            run_shell(command)
        else:
            command = 'echo ' + UserPass + ' | passwd --stdin ' + UserName+ ' &>/dev/null'
            run_shell(command)
         # 添加安全账户到sudoer组,基于安全账户sudo权限
        SD_Z = UserName+"    ALL=(ALL)    NOPASSWD: ALL"
        remove_line(SD_Z,self.path)
        append_line(SD_Z,self.path)
        # 给安全账户ssh权限
        command='mkdir -p /home/'+UserName+'/.ssh/ &&  chmod 700 /home/'+UserName+'/.ssh/'
        run_shell(command)
        if not os.path.exists('/home/'+UserName+'/.ssh/authorized_keys' ) and os.path.exists('/root/.ssh/authorized_keys'):
            cp_file('/root/.ssh/authorized_keys','/home/'+UserName+'/.ssh/authorized_keys',False)
            command='chmod 644 /home/'+UserName+ '/.ssh/authorized_keys && chown ' +UserName+'.'+UserName+' /home/' +UserName+'/.ssh/authorized_keys'
            run_shell(command,False)
        if not os.path.exists('/home/'+UserName+'/.ssh/id_rsa' ) and os.path.exists('/root/.ssh/id_rsa'):
            cp_file('/root/.ssh/id_rsa','/home/'+UserName+'/.ssh/id_rsa',False)
            command='chmod 600 /home/'+UserName+ '/.ssh/id_rsa && chown ' +UserName+'.'+UserName+' /home/' +UserName+'/.ssh/id_rsa'
            run_shell(command,False)
        if not os.path.exists('/home/'+UserName+'/.ssh/id_dsa' ) and os.path.exists('/root/.ssh/id_dsa'):
            cp_file('/root/.ssh/id_dsa','/home/'+UserName+'/.ssh/id_dsa',False)
            command='chmod 600 /home/'+UserName+ '/.ssh/id_dsa && chown ' +UserName+'.'+UserName+' /home/' +UserName+'/.ssh/id_dsa'
            run_shell(command,False)

    def check(self):
        UserName = self.config.UserName
        command = 'id ' + UserName + ' 2>/dev/null | wc -l'
        num = run_shell(command,False)[0]
        if num == '1' or num == 1:
            flag = True
            print('存在安全符合账户,账户名：', UserName)
        else:
            flag=False
        return flag
    
    def reset(self,backup_path=Initial_dir):
        self.recovery()

    def recovery(self,backup_path=Initial_dir):
        UserName = self.config.UserName
        command = 'userdel -f ' + UserName +' 2>/dev/null'
        run_shell(command, False)
        SD_Z = UserName + "    ALL=(ALL)    NOPASSWD: ALL"
        remove_line(SD_Z, self.path)
        if os.path.exists('/home/' +UserName):
            command='rm -rf '+'/home/' +UserName
            run_shell(command,False)


class SU_WHEEL(BaseFix): #限制部分用户不能使用su
    def __init__(self):
        super().__init__()
        self.id = 14
        self.path='/etc/pam.d/su'
        self.description='su权限的设定'

    def run(self):
        if os.path.exists(self.path):
            Strand = 'auth sufficient pam_rootok.so'
            StrandNum = len(grep_find(Strand, self.path))
            if StrandNum < 1:
                append_line(Strand, self.path)
            Strand = 'auth required pam_wheel.so group=wheel'
            StrandNum =len(grep_find( Strand,self.path))
            if StrandNum<1:
                append_line(Strand,self.path)

    def recovery(self,backup_path=Initial_dir):
        remove_line('auth sufficient pam_rootok.so',self.path)
        remove_line('auth required pam_wheel.so group=wheel',self.path)

    def check(self):
        flag1=False
        flag2=False
        if os.path.exists(self.path):
            Strand = 'auth required pam_wheel.so'
            StrandNum =len(grep_find( Strand,self.path))
            if StrandNum>=1:
                flag1=True
            Strand = 'auth sufficient pam_rootok.so'
            StrandNum = len(grep_find(Strand, self.path))
            if StrandNum >= 1:
                flag2 = True
        return flag1 and flag2
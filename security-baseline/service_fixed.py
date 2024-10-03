# 服务相关加固项，编号从21开始
import os.path

from do_shell import run_shell
from base_function import split_file_by_line,grep_find,sed_repalce,append_line,remove_line
from base_function import rm_file,cp_file,backup_file,reset_file,BaseFix
from base_function import replace_line,comment_out_line
from config import fixed_config
config=fixed_config()
Initial_dir=config.Initial_dir

class TELENT(BaseFix): #关闭telent安装openssh
    def __init__(self):
        super().__init__()
        self.id = 21
        self.path='/etc/xinetd.d/telnet'
        self.description='关闭telent，使用openssh'

    def run(self):
        if os.path.exists(self.path):
            flags=grep_find('^disable', self.path)
            for flag in flags:
                sed_repalce(flag,'disable = yes',self.path)
            run_shell('service xinetd restart')

        Ssh_num=run_shell('rpm -qa|grep openssh|wc -l')
        if int(Ssh_num[0])<=3:
            run_shell('yum -y install openssh &>/dev/null')

    def reset(self):
        if reset_file(Initial_dir, self.path):
            pass

    def recovery(self):
        reset_file(Initial_dir, self.path)
        if os.path.exists(self.path):
            sed_repalce('yes','disable',self.path)
        run_shell('service xinetd restart &>/dev/null')

    def check(self):
        if not os.path.exists(self.path):
            return True
        flags = grep_find('^disable', self.path)
        if flags==[]:
            return False
        else:
            if 'yes' in flags[-1]:
                return True
            else:
                return False


class ROOT_LOGIN(BaseFix): #限制root用户使用ssh登录
    def __init__(self):
        super().__init__()
        self.id = 22
        self.path='/etc/ssh/sshd_config'
        self.description='禁止root账户ssh登录'

    def run(self):
        flags=grep_find('PermitRootLogin',self.path)
        if flags!=[]:
            for flag in flags:
                if '#'!=flag[0]:
                    sed_repalce(flag,"PermitRootLogin no",self.path)
        else:
            append_line("PermitRootLogin no",self.path)

    def reset(self):
        if reset_file(Initial_dir, self.path):
            pass
        else:
            self.recovery()

    def recovery(self):
        flags = grep_find('PermitRootLogin', self.path)
        if flags != []:
            for flag in flags:
                if '#' != flag[0]:
                    sed_repalce(flag, "PermitRootLogin yes", self.path)
        else:
            append_line("PermitRootLogin yes", self.path)

    def check(self):
        flags = grep_find('^PermitRootLogin', self.path)
        if flags == []:
            return False
        else:
            if 'yes' in flags[-1]:
                return False
            else:
                return True


class SSH_PORT(BaseFix): #ssh端口修改为非22号端口
    def __init__(self):
        super().__init__()
        self.id = 23
        self.path='/etc/ssh/sshd_config'
        self.description='openssh端口修改为非22号端口'

    def run(self):
        command="setenforce 0 && sed -i 's#^SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config"
        run_shell(command)
        command='rpm -qa iptables*|wc -l'
        config=fixed_config()
        New_port=config.New_Port
        if int(run_shell(command,False)[0])>0:
            command='iptables -I INPUT  -p tcp -m state --state NEW -m tcp --dport '+New_port.split(' ')[-1]+ ' -j ACCEPT && service iptables save'
            run_shell(command)
        Old_Port_Num=int(run_shell("grep '^Port ' "+self.path+" 2>/dev/null|wc -l",False)[0])
        if Old_Port_Num==1:
            Old_Port = grep_find('^Port',self.path)
            sed_repalce(Old_Port[0],New_port,self.path)
        elif Old_Port_Num>1:
            Old_Port = grep_find('^Port', self.path)
            flag=0
            for Port in Old_Port:
                if flag==0:
                    sed_repalce(Port, New_port, self.path)
                    flag=1
                else:
                    remove_line(Port,self.path)
        else:
            append_line(New_port,self.path)
        run_shell('systemctl restart sshd')   #重启ssh服务确保修改生效

    def reset(self):
        if reset_file(Initial_dir, self.path):
            pass
        else:
            self.recovery()

    def recovery(self):
        command = "setenforce 0 && sed -i 's#^SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config"
        run_shell(command)
        Raw_port="Port 22"
        Old_Port_Num = int(run_shell("grep '^Port ' " + self.path + " 2>/dev/null|wc -l", False)[0])
        if Old_Port_Num == 1:
            Old_Port = grep_find('^Port', self.path)
            sed_repalce(Old_Port[0], Raw_port, self.path)
        elif Old_Port_Num > 1:
            Old_Port = grep_find('^Port', self.path)
            flag = 0
            for Port in Old_Port:
                if flag == 0:
                    sed_repalce(Port, Raw_port, self.path)
                    flag = 1
                else:
                    remove_line(Port, self.path)
        run_shell('systemctl restart sshd')  # 重启ssh服务确保修改生效

    def check(self):
        flags=grep_find('^Port',self.path)
        if flags==[]:
            return False
        if '10000' in flags[-1]:
            return True
        else:
            return False


class DEL_DANGER_FILE(BaseFix): #删除对系统安全构成威胁的文件
    def __init__(self):
        super().__init__()
        self.id = 24
        self.description='删除对.netrc，.rhosts的文件'

    def run(self):
        run_shell('find / -type f -name ".netrc"  2>/dev/null | xargs rm -f')
        run_shell('find / -type f -name ".rhosts" 2>/dev/null | xargs rm -f')

    def reset(self):
        if reset_file(Initial_dir, self.path):
            pass
        else:
            self.recovery()

    def recovery(self):
        pass

    def check(self):
        flag=True
        if int(run_shell('find / -type f -name ".netrc" 2>/dev/null | wc -l',False)[0])!=0:
            print ('存在.netrc类型的风险文件，需删除！')
            flag=False
        if int(run_shell('find / -type f -name ".rhosts" 2>/dev/null | wc -l',False)[0])!=0:
            print ('存在.rhosts类型的风险文件，需删除！')
            flag=False
        return flag


class CHECK_ICMP(BaseFix): #禁止响应ping，避免被扫描发现
    def __init__(self):
        super().__init__()
        self.id = 25
        self.path='/etc/sysctl.conf'
        self.description='禁止响应ping，避免被扫描发现'

    def run(self):
        Sysctl_Num=int(run_shell("grep '^net.ipv4.icmp_echo_ignore_all' "+self.path+"|wc -l")[0])
        if Sysctl_Num>=1:
            flag=0
            Sysctl=grep_find('^net.ipv4.icmp_echo_ignore_all',self.path)
            for ctl in Sysctl:
                if flag==0:
                    sed_repalce(ctl,'net.ipv4.icmp_echo_ignore_all = 1',self.path)
                    flag=1
                else:
                    remove_line(ctl,self.path)
        else:
            append_line('net.ipv4.icmp_echo_ignore_all = 1',self.path)
        run_shell('sysctl -p >/dev/null 2>&1',False)

    def reset(self):
        if reset_file(Initial_dir, self.path):
            pass
        else:
            self.recovery()

    def recovery(self):
        remove_line('^net.ipv4.icmp_echo_ignore_all',self.path)
        run_shell('sysctl -p >/dev/null 2>&1',False)

    def check(self):
        Sysctl = grep_find('^net.ipv4.icmp_echo_ignore_all', self.path)
        if Sysctl==[]:
            return False
        else:
            if '= 1' in Sysctl[-1] or '=1' in Sysctl[-1] or '=  1' in Sysctl[-1]:
                return True
            else:
                return False

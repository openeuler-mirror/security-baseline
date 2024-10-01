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

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

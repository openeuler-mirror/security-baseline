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

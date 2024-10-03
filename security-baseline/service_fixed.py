# 服务相关加固项，编号从21开始
import os.path

from do_shell import run_shell
from base_function import split_file_by_line,grep_find,sed_repalce,append_line,remove_line
from base_function import rm_file,cp_file,backup_file,reset_file,BaseFix
from base_function import replace_line,comment_out_line
from config import fixed_config
config=fixed_config()
Initial_dir=config.Initial_dir


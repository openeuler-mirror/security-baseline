# !/usr/bin/python3
##
# 系统安全检测加固工具 v1.0
###########################

import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='系统加固检测工具，请输入需要执行的操作和操作内容')
    parser.add_argument('--mode', dest='mode', type=str, help='设定工具运行模式：执行系统加固（fix），加固状态检测（check）、修复（recovery）和加固文件备份（backup）', default='check')
    parser.add_argument('--opt', dest='fixed_things', nargs='+', type=int, help='加固或者修复的数据项', default=[])
    parser.add_argument('--backup_path', dest='backup_path', type=str, help='用于设置备份的路径', default="/etc/._initialbak/")

    config=parser.parse_args()
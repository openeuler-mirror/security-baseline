# !/usr/bin/python3
##
# 系统安全检测加固工具 v1.0
###########################

import argparse
from mapping import catch_items
from base_function import print_line,cprint





def run(items,config):
    mode=config.mode
    fix_things=config.fixed_things
    if mode=='fix':
        print('执行系统加固')
        print_line()
        for key in items.keys():
            if fix_things==[] or key in fix_things:
                items[key][0].backup(False)
                print('执行编号',items[key][0].id,'加固,内容为',items[key][0].description)
                items[key][0].run()
                print_line()
    elif mode=='backup':
        print('执行加固需操作文件备份')
        print_line()
        for key in items.keys():
            if fix_things == [] or key in fix_things:
                items[key][0].backup()
    elif mode=='check':
        print('执行加固状态检测')
        print_line()
        for key in items.keys():
            if fix_things == [] or key in fix_things:
                print_line()
                print('检测加固项,编号',key,',名称：',items[key][0].description)
                print_line(False)
                if items[key][0].check():
                    print('满足加固需求。')
                else:
                    cprint('注意：该加固项检测未通过。','red')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='系统加固检测工具，请输入需要执行的操作和操作内容')
    parser.add_argument('--mode', dest='mode', type=str, help='设定工具运行模式：执行系统加固（fix），加固状态检测（check）、修复（recovery）和加固文件备份（backup）', default='check')
    parser.add_argument('--opt', dest='fixed_things', nargs='+', type=int, help='加固或者修复的数据项', default=[])
    parser.add_argument('--backup_path', dest='backup_path', type=str, help='用于设置备份的路径', default="/etc/._initialbak/")

    config=parser.parse_args()
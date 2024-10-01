# !/usr/bin/python3
##
# 系统安全检测加固工具 v1.0
###########################

import argparse
from mapping import catch_items
from base_function import print_config,print_desc,print_line,cprint




def run(items,config):
    if config.need_version:
        print('0.1.1-8\n')
        return 
    mode=config.mode
    fix_things=config.fixed_things
    force=config.force_backup
    backup_path=config.backup_path
    if mode=='fix':
        print('执行系统加固')
        print_line()
        for key in items.keys():
            if fix_things==[] or key in fix_things:
                items[key][0].backup(backup_path=backup_path,force=force,show=True)
                print('执行编号',items[key][0].id,'加固,内容为',items[key][0].description)
                items[key][0].run()
                print_line()
    elif mode=='backup':
        print('执行加固需操作文件备份')
        print_line()
        for key in items.keys():
            if fix_things == [] or key in fix_things:
                items[key][0].backup(backup_path=backup_path,force=force,show=True)
    elif mode=='recovery':
        print('执行加固项数值修复')
        print_line()
        for key in items.keys():
            if fix_things == [] or key in fix_things:
                items[key][0].recovery(backup_path=backup_path)
                print('修复编号为', items[key][0].id, '的加固项')
        print_line()
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
    elif mode=='reset':
        print('执行加固操作文件还原')
        print_line()
        
        for key in items.keys():
            if fix_things == [] or key in fix_things:
                items[key][0].reset(backup_path=backup_path)
        print('已完成,加固操作文件还原。')
    else:
        print('展示加固相关设置和内容')
        print_config(config)
        print_desc(fixed_items)
       #只显示加固项内容



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='系统加固检测工具,请输入需要执行的操作和操作内容')
    parser.add_argument('--mode', dest='mode', type=str, help='设定工具运行模式: 执行系统加固(fix),加固状态检测(check),修复(recovery)和加固文件备份(backup)', default='check')
    parser.add_argument('--opt', dest='fixed_things', nargs='+', type=int, help='加固或者修复的数据项', default=[])
    parser.add_argument('--force', dest='force_backup', action="store_true", help='强制备份设置项', default=True)
    parser.add_argument('--backup_path', dest='backup_path', type=str, help='用于设置备份的路径', default="/etc/._initialbak/")
    parser.add_argument('--version', '-V',dest='need_version',action="store_true", help='版本号查询', default=False)

    config=parser.parse_args()
    fixed_items= catch_items()
    fixed_ids=list(fixed_items.keys())
    run(fixed_items,config)

    #if config.mode=='fix':
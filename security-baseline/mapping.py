"""
 (c) 2024 - Copyright CTyunOS Inc

 Authors:
   wukaishun <wuksh@chinatelecom.cn>

"""
#功能映射模块,实现自动映射加固项和编号
from account_fixed import *
from service_fixed import *
import account_fixed
import service_fixed



def catch_items():
    account_fix_items=dir(account_fixed)
    service_fixed_items=dir(service_fixed)
    repair_items=[item for item in account_fix_items if item not in service_fixed_items]+\
            [item for item in service_fixed_items if item not in account_fix_items]

    fix_items={}
    for item in repair_items:
        fix_item=eval(item)()
        fix_items[fix_item.id]=[fix_item,item]
    fix_items=dict(sorted(fix_items.items(), key=lambda x: x[0]))
    return fix_items


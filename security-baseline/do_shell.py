#提供python执行shell脚本的功能,并输出
import subprocess
import os

#input: run_shell(command,True/False) #单条shell指令,是否显示输出结果


def run_shell(do,show_state=True):
    result=os.popen(do)
    output=[]
    for l in result.readlines():
        output.append(l.split('\n')[0])
        if show_state:
            print(output[-1])
    return output


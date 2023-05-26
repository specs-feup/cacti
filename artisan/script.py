from meta_cl import *
import time


def print_time(time):
    print("CACTI:"+str(round(time-start_time,2))+":CACTI\n")

start_time= time.time()

try : 
    ast = Ast('src.cpp')
except:
    parse_time=time.time()
    print("CACTI:Error parse!:CACTI")
    print_time(parse_time)
else:
    parse_time=time.time()
    print("CACTI:File parsed correctly!:CACTI")
    print_time(parse_time)
    try:
        result = ast.unparse()
    except:
        code_gen_time = time.time()
        print("CACTI:Error code generation!:CACTI")
        print_time(code_gen_time)      
    else: 
        code_gen_time = time.time()
        print("CACTI:Code generated correctly!:CACTI")
        print_time(code_gen_time)
        print("CACTI:"+result+":CACTI")

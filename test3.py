from inspect import getmembers, isfunction,getcomments
import inspect
import test1


for FunctionName,Function in getmembers(test1, isfunction):
    print(FunctionName)
    print(inspect.getfullargspec(Function)[3])
    for kkk in inspect.getfullargspec(Function)[3]:
        print(type(kkk))
        print(type(kkk) == float)
        print(type(kkk) == list)
        print(type(kkk) == bool)
        print(type(kkk) == str)
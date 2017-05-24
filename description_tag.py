# -*- coding: utf-8 -*
from functools import wraps

def log(f):
    def wrap(*args, **kwargs):
        print 'hello log'
        return f(*args, **kwargs)
    return wrap

def log2(text):
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            print 'hello log2'
            print text
            return f(*args, **kwargs)
        return wrap
    return decorator

@log2('lallala')
def now():
    print 'hello now'



if __name__ == '__main__':
    now()
    print now.__name__
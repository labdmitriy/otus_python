#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper, wraps


def disable(deco):
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    '''
    
    return


# Not working
def decorator(deco):
    '''
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    '''
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            result = deco(func(*args, **kwargs))
            return result
        update_wrapper(wrapper, func)
        return wrapper
    #return real_decorator

def countcalls(func):
    '''Decorator that counts calls made to the function decorated.'''
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    
    return wrapper

# Not working
def memo(func):
    '''
    Memoize a function so that it caches all return values for
    faster future lookups.
    '''
    cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args not in cache:
            cache[args] = func(*args, **kwargs)
        return cache[args]
    # update_wrapper(wrapper, func)
    return wrapper


def n_ary(func):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''
    def wrapper(*args, **kwargs):
        args_count = len(args)
        
        if args_count > 2:
            x, y = args[-2:]
            args = args[:-2]
            res = func(x, y)
            
            while(args):
                res = func(args[-1], res, **kwargs)
                args = args[:-1]
                
            return res
        elif args_count == 2:
            return func(*args)
        elif args_count == 1:
            return args[0]
        else:
            return None
    
    return wrapper


def trace():
    '''Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    '''
    return

@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
#@trace("####")
@memo
def fib(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print foo(4, 3)
    print foo(4, 3, 2)
    print foo(4, 3)
    print "foo was called", foo.calls, "times"

    print bar(4, 3)
    print bar(4, 3, 2)
    print bar(4, 3, 2, 1)
    print "bar was called", bar.calls, "times"

    print fib.__doc__
    fib(3)

    print fib.calls, 'calls made'


if __name__ == '__main__':
    main()

import functools
import types


def copy_func(f):  # type: ignore
    n = types.FunctionType(
        f.__code__,
        f.__globals__,
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    n = functools.update_wrapper(n, f)
    n.__kwdefaults__ = f.__kwdefaults__
    return n

from collections import OrderedDict
from functools import wraps
import unittest
import inspect


class Context(object):
    pass


def spec(func):

    def get_spec_steps(test_func, self):

        def to_action(name, code):

            def runner_empty(context): pass
            def runner_with_self(context): self  # placeholder for a function with self closure

            runner = runner_empty if len(code.co_freevars) == 0 else runner_with_self
            runner.__name__ = name
            runner.__code__ = code
            runner.__globals__.update(test_func.__globals__)
            return runner

        steps = OrderedDict()
        for fn_def in test_func.__code__.co_consts:
            if inspect.iscode(fn_def) and _is_step_name(fn_def.co_name):
                steps[fn_def.co_name] = to_action(fn_def.co_name, fn_def)

        return steps

    @wraps(func)
    def run_spec(*args, **kwargs):

        self = next(iter(args or []), None)

        context = Context()

        _call_test_function(func, context, *args, **kwargs)

        test_func = _get_original_func(func)  # we need to get to the test function to find spec step methods
        steps = get_spec_steps(test_func, self)
        if len(steps) == 0:
            return

        _output_step("* SPEC: ", test_func)

        try:
            for name, section in steps.items():

                if name.startswith("given"):
                    _output_step("  ", section)
                    section(context)

                if name.startswith("when"):
                    _output_step("  ", section)
                    section(context)

                if name.startswith("it_should"):
                    _output_step("    > ", section)
                    section(context)
        finally:
            cleanups = _get_all_named_like(steps, "cleanup")
            for cleanup in cleanups:
                _output_step("  ", cleanup)
                cleanup(context)

    return run_spec


class MetaSpec(type):

    def __new__(mcs, clsname, bases, attrs):

        decorated_attrs = {}
        for name, val in attrs.items():
            if name.startswith("test_") and inspect.isroutine(val):
                decorated_attrs[name.replace("_", " ")] = spec(val)
            else:
                decorated_attrs[name] = val

        return super(MetaSpec, mcs).__new__(mcs, clsname, bases, decorated_attrs)

    def __getattr__(self, name):
        return _get_spaced_test(self, name)


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    class Metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(Metaclass, 'temporary_class', (), {})


class SpecTestCase(with_metaclass(MetaSpec, unittest.TestCase)):

    def __getattr__(self, name):
        return _get_spaced_test(self, name)


def _is_step_name(name):
    return name.startswith("given")\
        or name.startswith("when")\
        or name.startswith("it_should")\
        or name.startswith("cleanup")


def _get_original_func(func):
    if isinstance(func, (classmethod, staticmethod)):
        return func.__func__

    # get original func from decorators (only for those who follow standard update_wrapper/wraps pattern)
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func


def _call_test_function(func, context, *args, **kwargs):
    args_names = inspect.getargspec(_get_original_func(func))[0]
    if "ctx" in args_names:
        kwargs["ctx"] = context

    if isinstance(func, (classmethod, staticmethod)):
        self = args[0]
        args = args[1:]
        func = func.__get__(self, type(self))  # we need to call underlying static or class function

    func(*args, **kwargs)


def _get_all_named_like(dict_, name):
    return [v for k, v in dict_.items() if k.startswith(name)]


def _output_step(message, func):
    func_name = func.__name__.replace("_", " ")
    print(message + func_name)


def _get_spaced_test(self, name):
    if name.startswith("test_"):
        spaced_name = name.replace("_", " ")
        return getattr(self, spaced_name)

    raise AttributeError("%r object has no attribute %r" % (self.__class__, name))

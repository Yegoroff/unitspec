from functools import wraps
import unittest
import inspect


class Context(object):
    pass

def _is_spec_name(name):
    return name.startswith("given")\
        or name.startswith("when")\
        or name.startswith("it_should")\
        or name.startswith("cleanup")

def get_all_by_partial(dict, partial_key):
    return [v for k,v in dict.items() if k.startswith(partial_key)]

def get_by_partial(dict, partial_key):
    values = get_all_by_partial(dict, partial_key)
    return values[0] if values else None

def spec(func):

    def get_specs(self):

        def to_action(name, code):

            def runner_empty(context):pass
            def runner_with_self(context):self

            runner = runner_empty if len(code.co_freevars) == 0 else runner_with_self
            runner.__name__ = name
            runner.__code__ = code
            runner.__globals__.update(func.__globals__)
            return runner

        specs = {}
        for fn_def in func.__code__.co_consts:
            if inspect.iscode(fn_def) and _is_spec_name(fn_def.co_name):
                specs[fn_def.co_name] = to_action(fn_def.co_name, fn_def)

        return specs

    @wraps(func)
    def run_specs(self):

        context = Context()

        if func.__code__.co_argcount == 2:
            func(self, context)
        else:
            func(self)

        specs = get_specs(self)
        if len(specs) == 0:
            return

        output_stage("* SPEC: ", func)

        try:
            given = get_by_partial(specs, "given")
            if given:
                output_stage("  ", given)
                given(context)

            when = get_by_partial(specs, "when")
            if when:
                output_stage ("  ", when)
                when(context)

            for should in get_all_by_partial(specs, "it_should"):
                output_stage ("    > ", should)
                should(context)

        finally:
            cleanup = get_by_partial(specs, "cleanup")
            if cleanup:
                output_stage ("  ", cleanup)
                cleanup(context)

    return run_specs


def output_stage(message, func):
    func_name = func.__name__.replace("_", " ")
    print(message + func_name)

def get_spaced_test(self, name):
    if name.startswith("test_"):
        spaced_name = name.replace("_", " ")
        return getattr(self, spaced_name)

    raise AttributeError("%r object has no attribute %r" % (self.__class__, name))


class MetaSpec(type):

    def __new__(cls, clsname, bases, attrs):

        decorated_attrs = {}
        for name, val in attrs.items():
            if name.startswith("test_") and inspect.isfunction(val):
                decorated_attrs[name.replace("_", " ") ] = spec(val)
            else:
                decorated_attrs[name] = val

        return super(MetaSpec, cls).__new__(cls, clsname, bases, decorated_attrs)

    def __getattr__(self, name):
        return get_spaced_test(self, name)


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    class metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


class SpecTestCase(with_metaclass(MetaSpec,unittest.TestCase)):

    def __getattr__(self, name):
        return get_spaced_test(self, name)


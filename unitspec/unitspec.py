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
            runner.func_name = name
            runner.func_code = code
            runner.func_globals.update(func.func_globals)
            return runner

        specs = {}
        for fn_def in func.func_code.co_consts:
            if inspect.iscode(fn_def) and _is_spec_name(fn_def.co_name):
                specs[fn_def.co_name] = to_action(fn_def.co_name, fn_def)

        return specs

    @wraps(func)
    def run_specs(self):

        context = Context()

        if func.func_code.co_argcount == 2:
            func(self, context)
        else:
            func(self)

        specs = get_specs(self)
        if len(specs) == 0:
            return

        print "* SPEC: " + func.func_name.replace("_", " ")

        try:
            given = get_by_partial(specs, "given")
            if given:
                print "  " + given.func_name.replace("_", " ")
                given(context)

            when = get_by_partial(specs, "when")
            if when:
                print "  " + when.func_name.replace("_", " ")
                when(context)

            for should in get_all_by_partial(specs, "it_should"):
                print "    > " + should.func_name.replace("_", " ")
                should(context)

        finally:
            cleanup = get_by_partial(specs, "cleanup")
            if cleanup:
                print "  " + cleanup.func_name.replace("_", " ")
                cleanup(context)

    return run_specs


def get_spaced_test(self, name):
    if name.startswith("test_"):
        spaced_name = name.replace("_", " ")
        return getattr(self, spaced_name)

    raise AttributeError("%r object has no attribute %r" % (self.__class__, name))


class MetaSpec(type):

    def __new__(cls, clsname, bases, attrs):

        decorated_attrs = {}
        for name, val in attrs.iteritems():
            if name.startswith("test_") and inspect.isfunction(val):
                decorated_attrs[name.replace("_", " ") ] = spec(val)
            else:
                decorated_attrs[name] = val

        return super(MetaSpec, cls).__new__(cls, clsname, bases, decorated_attrs)

    def __getattr__(self, name):
        return get_spaced_test(self, name)


class SpecTestCase(unittest.TestCase):

    __metaclass__ = MetaSpec

    def __getattr__(self, name):
        return get_spaced_test(self, name)

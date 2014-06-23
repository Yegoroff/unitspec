import unittest
import inspect

class Context(object):
    pass

def _is_spec_name(name):
    return name in ["given", "when"] or name.startswith("it_should")

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

        given = specs.get("given", None)
        if given: given(context)

        when = specs.get("when", None)
        if when: when(context)

        for should in specs:
            if should.startswith("it_should"):
                print "    > " + should.replace("_", " ")
                specs[should](context)

    return run_specs


class MetaSpec(type):

    def __new__(cls, clsname, bases, attrs):

        decorated_attrs = {}
        for name, val in attrs.iteritems():
            if name.startswith("test_") and inspect.isfunction(val):
                decorated_attrs[name.replace("_", " ") ] = spec(val)
            else:
                decorated_attrs[name] = val

        return super(MetaSpec, cls).__new__(cls, clsname, bases, decorated_attrs)


class SpecTestCase(unittest.TestCase):

    __metaclass__ = MetaSpec

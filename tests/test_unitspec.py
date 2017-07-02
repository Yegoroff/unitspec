from functools import wraps
from mock import patch

from unitspec import SpecTestCase, spec, unitspec
from .scope_tets import scope_test


module_var = "module_scope"


def set_self_test_value(test_value=None):
    def func_wrapper(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, "test_value"):
                self.test_value = self.test_value + test_value
            else:
                self.test_value = test_value
            return func(self, *args, **kwargs)
        return wrapper
    return func_wrapper


# noinspection PyUnusedLocal
class UnitSpecTests(SpecTestCase):

    testcase_var = "testcase_scope"

    def test_sample_spec(self, ctx):

        ctx.value = "A"

        def given_string_AB(ctx):
            ctx.value += "B"

        def when_adding_C(ctx):
            ctx.result = ctx.value + "C"

        def it_should_be_ABC(ctx):
            self.assertEqual(ctx.result, "ABC")

        def it_should_not_be_AB(ctx):
            self.assertNotEqual(ctx.result, "AB")


    def test_incomplete_speck(self):

        def given(ctx):
            ctx.value = "A"

        def it_should_run_successful(ctx):
            self.assertEqual(ctx.value, "A")


    def test_cleanup(self):

        @spec
        def the_cleanup_test_body(self):

            def given(ctx):
                ctx.value = "1"

            def when(ctx):
                ctx.value += "2"

            def it_should_pass(ctx):
                self.assertEqual(ctx.value, "12")

            def cleanup_everything(ctx):
                self.cleaned_up = True

        self.cleaned_up = False

        the_cleanup_test_body(self)

        self.assertEqual(self.cleaned_up, True)


    def test_cleanup_after_failure(self):

        @spec
        def the_cleanup_test_body(self):

            def when_raising_exceptions(ctx):
                raise Exception("Should run cleanup")

            def cleanup_anyway(ctx):
                self.cleaned_up = True

        self.cleaned_up = False
        with self.assertRaises(Exception):
            the_cleanup_test_body(self)
        self.assertEqual(self.cleaned_up, True)


    def test_cleanup_after_assertions(self):

        @spec
        def the_cleanup_test_body(self):

            def it_should_fail(ctx):
                self.assertEqual(True, False)

            def cleanup_anyway(ctx):
                self.cleaned_up = True

        self.cleaned_up = False

        with self.assertRaises(AssertionError):
            the_cleanup_test_body(self)

        self.assertEqual(self.cleaned_up, True)


    def test_scope(self):

        def it_should_access_global_scope(ctx):
            self.assertEqual(scope_test(), "import_scope")

        def it_should_access_testcase_scope(ctx):
            self.assertEqual(self.testcase_var, "testcase_scope")

        def it_should_access_module_scope(ctx):
            self.assertEqual(module_var, "module_scope")


    def test_it_should_pass_regular_unittest(self):

        self.assertEqual("A", "A")


    def test_it_should_ignore_nested_user_defined_functions(self):

        def modify_val(val, modifier):
            return val + modifier

        value = modify_val("A", "B")
        self.assertEqual(value, "AB")


    def test_self_getattr_returns_attributes_by_declared_name(self):

        attr = getattr(self, "test_self_getattr_returns_attributes_by_declared_name")

        assert attr == self.test_self_getattr_returns_attributes_by_declared_name


    def test_cls_getattr_returns_attributes_by_declared_name(self):

        cls = type(self)
        attr = getattr(cls, "test_cls_getattr_returns_attributes_by_declared_name")

        assert attr == cls.test_cls_getattr_returns_attributes_by_declared_name


    def test_get_all_named_like(self):
        sample_dict = {"given_context": "a"}

        value = unitspec._get_all_named_like(sample_dict, "given")
        self.assertEqual(["a"], value)

        value = unitspec._get_all_named_like(sample_dict, "notexisting")
        self.assertEqual([], value)


    def test_ordered_spec_execution(self, ctx):

        ctx.order = 1

        def cleanup_last_8(ctx):
            self.assertEqual(8, ctx.order)

        def given_1(ctx):
            self.assertEqual(1, ctx.order)
            ctx.order += 1

        def given_2(ctx):
            self.assertEqual(2, ctx.order)
            ctx.order += 1

        def when_3(ctx):
            self.assertEqual(3, ctx.order)
            ctx.order += 1

        def it_should_be_4(ctx):
            self.assertEqual(4, ctx.order)
            ctx.order += 1

        def it_should_be_5(ctx):
            self.assertEqual(5, ctx.order)
            ctx.order += 1

        def when_6(ctx):
            self.assertEqual(6, ctx.order)
            ctx.order += 1

        def it_should_be_7(ctx):
            self.assertEqual(7, ctx.order)
            ctx.order += 1


    @staticmethod
    def test_staticmethod_spec_tests():

        def given_string_AB(ctx):
            ctx.value = "AB"

        def when_adding_C(ctx):
            ctx.value += "C"

        def it_should_be_ABC(ctx):
            assert(ctx.value == "ABC")


    @classmethod
    def test_classmethod_spec_tests(cls):

        assert(cls == UnitSpecTests)

        def given_string_AB(ctx):
            ctx.value = "AB"

        def when_adding_C(ctx):
            ctx.value += "C"

        def it_should_be_ABC(ctx):
            assert(ctx.value == "ABC")


    @set_self_test_value(test_value="One ")
    @set_self_test_value(test_value="Two")
    def test_it_invokes_decorators(self):

        self.assertEqual(self.test_value, "One Two")


    @set_self_test_value(test_value="One ")
    @set_self_test_value(test_value="Two")
    def test_it_calls_specs_within_decorated_tests(self):

        def it_should_call_specs_after_decorators(ctx):
            self.assertEqual(self.test_value, "One Two")


class MockTest(object):

    @classmethod
    def get_value(cls):
        return 1


class MockingSpecTests(SpecTestCase):

    @patch.multiple(MockTest, get_value=lambda: 2)
    def test_mocks_called_before_test_function(self):
        v = MockTest.get_value()
        self.assertEqual(v, 2)


    @patch.object(MockTest, 'get_value', return_value=5)
    @patch.object(MockTest, 'get_value', return_value=0)
    def test_mock_params_handled_correctly(self, mock1, mock2, ctx):

        ctx.v = MockTest.get_value()
        self.assertEqual(ctx.v, 5)

        def it_should_pass(ctx):
            self.assertEqual(ctx.v, 5)

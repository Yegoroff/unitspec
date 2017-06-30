from .scope_tets import scope_test
from unitspec import unitspec, spec
from unitspec import SpecTestCase


module_var = "module_scope"


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

        value = unitspec.get_all_named_like(sample_dict, "given")
        self.assertEqual(["a"], value)

        value = unitspec.get_all_named_like(sample_dict, "notexisting")
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
    def test_static_method_tests():

        def given_string_AB(ctx):
            ctx.value = "AB"

        def when_adding_C(ctx):
            ctx.value += "C"

        def it_should_be_ABC(ctx):
            assert(ctx.value == "ABC")


    @classmethod
    def test_class_method_tests(cls):

        def given_static_context_string_AB(ctx):
            ctx.value = "AB"

        def when_adding_C(ctx):
            ctx.value += "C"

        def it_should_be_ABC(ctx):
            assert(ctx.value == "ABC")

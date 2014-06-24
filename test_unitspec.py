from scope_tets import scope_test
from unitspec import SpecTestCase


module_var = "module_scope"

# noinspection PyUnusedLocal
class UnitSpecTests(SpecTestCase):

    testcase_var = "testcase_scope"

    def test_sample_spec(self, ctx):

        ctx.value = "A"

        def given(ctx):
           ctx.value += "B"

        def when(ctx):
            ctx.result = ctx.value + "C"

        def it_should_be_ABC(ctx):
            self.assertEqual(ctx.result, "ABC")

        def it_should_not_be_AB(ctx):
            self.assertNotEqual(ctx.result, "AB")


    def test_partial_speck(self):

        def given(ctx):
            ctx.value = "A"

        def it_should_run_successful(ctx):
            self.assertEqual(ctx.value, "A")


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

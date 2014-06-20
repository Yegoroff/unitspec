from scope_tets import module_test
from unitspec import SpecTestCase


module_var = "module_var"

# noinspection PyUnusedLocal
class UnitSpecTests(SpecTestCase):

    test_field = "test_field"

    def test_sample_spec(self):

        def establish(ctx):
            ctx.value = "A"

        def act(ctx):
            ctx.value += "B"

        def it_should_be_AB(ctx):
            self.assertEqual(ctx.value, "AB")

        def it_should_not_be_ABC(ctx):
            self.assertNotEqual(ctx.value, "ABC")

    def test_scope(self):

        def it_should_access_global_scope(ctx):
            self.assertEqual(module_test(), "module_test")

        def it_should_access_testcase_scope(ctx):
           self.assertEqual(self.test_field, "test_field")

        def it_should_access_module_scope(ctx):
            self.assertEqual(module_var, "module_var")

    def test_it_should_pass_regular_unittest(self):
        self.assertEqual("A", "A")


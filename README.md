unitspec
========

Specification tests within Python unittests


Sample:

```python

from unitspec import SpecTestCase

class UnitSpecTests(SpecTestCase):

    def test_string_addition(self, ctx):

        ctx.value = "A"

        def given_string_AB(ctx):
           ctx.value += "B"

        def when_adding_C(ctx):
            ctx.result = ctx.value + "C"

        def it_should_be_ABC(ctx):
            self.assertEqual(ctx.result, "ABC")

        def it_should_not_be_AB(ctx):
            self.assertNotEqual(ctx.result, "AB")

        def cleanup_after_test(ctx):
            ctx.value = None

```

the output will be:
```
* SPEC: test sample spec
  given string AB
  when adding C
    > it should be ABC
    > it should not be AB
  cleanup after test
```

descendants of the 'SpecTestCase' allowed to combine common unittest methods with the spec-based.

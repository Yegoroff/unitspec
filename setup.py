from setuptools import setup, find_packages
import unitspec


setup(
    name='unitspec',
    version=unitspec.__version__,
    author="Alexander Yegorov",
    description="Specification tests within Python unittests",
    long_description="Specification tests within Python unittests",
    packages=find_packages(exclude=("tests",)),
    url="https://github.com/Yegoroff/unitspec",
    include_package_data=True,
    zip_safe=False,
    license = "MIT"
)
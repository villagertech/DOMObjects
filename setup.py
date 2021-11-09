from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


long_description = read('README.rst')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='DOMObjects',
    version='v0.1.0b4',
    url='https://github.com/villagertech/DOMObjects',
    project_urls={
        "Bug Tracker": 'https://github.com/villagertech/DOMObjects/issues'
    },
    license='MIT',
    author='Rob MacKinnon',
    author_email='rome@villagertech.com',
    python_requires=">=3.6",
    platforms='any',
    tests_require=['pytest'],
    install_requires=[],
    cmdclass={'test': PyTest},
    description='Create Python DOM style datastructures with ease.',
    long_description=long_description,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    test_suite='',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
        ],
    extras_require={
        'testing': ['pytest'],
    }
)

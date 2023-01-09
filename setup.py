#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""The setup script."""

import io
import os
import pathlib
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup
from setuptools.dist import Distribution


REGEXP = re.compile(r'^__version__\W*=\W*"([\d.abrc]+)"')
PARENT = pathlib.Path(__file__).parent

requirements = ['click', ]
test_requirements = ['pytest>=3', ]
setup_requirements = ['pytest-runner', 'setuptools_scm>=3.3.1', ]


class BinaryDistribution(Distribution):
    """Distribution which almost always forces a binary package with platform name"""

    def has_ext_modules(self):
        """Ensure it has ext modules."""
        return super().has_ext_modules() or not os.environ.get('SETUPPY_ALLOW_PURE')


def read(*names, **kwargs):
    """Read a file."""
    with io.open(join(dirname(__file__), *names),
                 encoding=kwargs.get('encoding', 'utf8')) as file_handler:
        return file_handler.read()


def read_version():
    """read_version."""
    init_py = os.path.join(
        os.path.dirname(__file__), "src", "better_crypto", "__init__.py"
    )

    with open(init_py, encoding="utf-8") as open_file:
        for line in open_file:
            match = REGEXP.match(line)
            if match is not None:
                return match.group(1)
        msg = f"Cannot find version in ${init_py}"
        raise RuntimeError(msg)


def read_requirements(path: str):
    """read_requirements."""
    file_path = PARENT / path
    with open(file_path, encoding="utf-8") as open_file:
        return open_file.read().split("\n")


if __name__ == "__main__":
    setup(
        name='trending-homebrew',
        use_scm_version={
            'local_scheme': 'dirty-tag',
            'write_to': 'src/trending_homebrew/_version.py',
            'fallback_version': '0.1.0',
        },
        license='MIT',
        description='Tool for identifying trending Homebrew formulae, casks, and build errors.',
        long_description='{}\n{}'.format(
            re.compile('^.. start-badges.*^.. end-badges',
                       re.M | re.S).sub('', read('README.rst')),
            re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst')),
        ),
        author='John Patrick Roach',
        author_email='contact@johnpatrickroach.com',
        url='https://github.com/johnpatrickroach/trending-homebrew',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
        include_package_data=True,
        zip_safe=False,
        classifiers=[
            # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
            'Development Status :: 4 - Beta',
            'Environment :: MacOS X',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: MacOS',
            'Operating System :: Unix',
            'Operating System :: POSIX',
            'Operating System :: Microsoft :: Windows',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Ruby',
            # uncomment if you test on these interpreters:
            # 'Programming Language :: Python :: Implementation :: IronPython',
            # 'Programming Language :: Python :: Implementation :: Jython',
            # 'Programming Language :: Python :: Implementation :: Stackless',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: System :: Installation/Setup',
            'Topic :: System :: Software Distribution',
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
        ],
        project_urls={
            'Documentation': 'https://trending-homebrew.readthedocs.io/',
            'Changelog': 'https://trending-homebrew.readthedocs.io/en/latest/changelog.html',
            'Issue Tracker': 'https://github.com/johnpatrickroach/trending-homebrew/issues',
        },
        keywords=[
            'homebrew', 'formulae', 'formula', 'casks', 'cask',
            'build', 'builds', 'error', 'errors', 'count', 'counts',
            'installs', 'items', 'trends', 'trending', 'top', 'macos',
            'brews', 'brew', 'tap', 'taps', 'cli', 'python', 'package',
            'pypi', 'pip', 'johnpatrickroach', 'better-wealth',
            'trending-homebrew', 'trending_homebrew', 'install'
        ],
        python_requires='>=3.7',
        install_requires=read_requirements("requirements/production.txt"),
        test_suite='tests',
        tests_require=test_requirements,
        extras_require={
            # eg:
            #   'rst': ['docutils>=0.11'],
            #   ':python_version=="2.6"': ['argparse'],
        },
        setup_requires=setup_requirements,
        entry_points={
            'console_scripts': [
                'trending-homebrew = trending_homebrew.cli:main',
            ]
        },
        distclass=BinaryDistribution,
    )

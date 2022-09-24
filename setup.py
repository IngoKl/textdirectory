#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['click', 'numpy', 'requests', 'beautifulsoup4', 'spacy', 'psutil', 'en_core_web_sm', 'twine', 'lxml', 'tqdm']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', 'numpy', 'spacy', 'psutil', 'en_core_web_sm', ]

setup(
    author="Ingo Kleiber",
    author_email='ingo@kleiber.me',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="TextDirectory allows you to combine multiple text files into one. While doing this, filters and transformations can be applied.",
    entry_points={
        'console_scripts': [
            'textdirectory=textdirectory.cli:main',
        ],
    },
    dependency_links=[
        'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.1.0/en_core_web_sm-3.1.0-py3-none-any.whl'
    ],
    install_requires=requirements,
    license='MIT license',
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='textdirectory',
    name='textdirectory',
    packages=find_packages(include=['textdirectory']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/IngoKl/textdirectory',
    version='0.3.3',
    zip_safe=False,
)

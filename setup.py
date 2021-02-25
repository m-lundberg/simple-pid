from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='simple-pid',
    version='0.2.4',
    description='A simple, easy to use PID controller',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/m-lundberg/simple-pid',
    author='Martin Lundberg',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='pid controller control',
    packages=find_packages(),
    package_data={
        'simple_pid': ['*.pyi', 'py.typed'],
    },
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'docs': ['m2r', 'sphinx-rtd-theme']
    },
    project_urls={
        'Documentation': 'https://simple-pid.readthedocs.io/',
    },
)

import os
from setuptools import find_packages, setup

import popup_field

version = popup_field.__version__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

with open(os.path.join(os.path.dirname(__file__), 'HISTORY.md')) as history:
    HISTORY = history.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-popup-field',
    version=version,
    description='A popup field for django which can create\update\delete ForeignKey and ManyToManyField instance by popup windows.',
    long_description=README + '\n\n' + HISTORY,
    license='BSD 3-Clause License',
    packages=[
        'popup_field'
    ],
    include_package_data=True,
    install_requires=[
    ],
    url='https://github.com/yinkh/django-popup-field.git',
    author='Yin KangHong',
    author_email='614457662@qq.com',
    keywords='django-popup-field',
    classifiers=[
        'Development Status :: 0.1 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
)

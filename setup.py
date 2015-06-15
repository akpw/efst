## Copyright (c) 2014 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

from setuptools import setup, find_packages

setup(
    name='efst',
    version='0.23',

    url='https://github.com/akpw/efst',

    author='Arseniy Kuznetsov',
    author_email='k.arseniy@gmail.com',

    description=('''
                    Encrypted File System CLI Tools, to secure and manage your data with EncFS
                '''),
    license='GNU General Public License v2 (GPLv2)',

    packages=find_packages(exclude=['test*']),

    package_data = {
        '': ['config/*.conf'],
    },

    keywords = 'EncFS create manage encrypt decrypt export mount unmount ciphertext plaintext',

    install_requires = ['configobj>=5.0.6', 'keyring>=5.3', 'pexpect>=3.3'],

    test_suite = 'tests.efst_test_suite',

    entry_points={'console_scripts': [
        'efst = efst.cli.efst.efst_dispatch:main',
        'efsc = efst.cli.efsc.efsc_dispatch:main',
        'efsm = efst.cli.efsm.efsm_dispatch:main',
    ]},

    zip_safe=True,

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Topic :: System',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ]
)




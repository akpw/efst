#!/usr/bin/env python
# coding=utf8
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

''' EncFS install check
'''

import sys
from efst.encfs.encfs_cfg import EncFSUtils, EncFSNotInstalled

def check_encfs_installed():
    if not EncFSUtils.encfs_installed():
        print(EncFSNotInstalled().default_message)
        sys.exit(0)

# check encfs installed
check_encfs_installed()


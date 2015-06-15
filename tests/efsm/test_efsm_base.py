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

import os
from ..base import test_base
from efst.config.efst_config import ConfigEntries, EntryTypes


class EFSMTest(test_base.BMPTest):
    @classmethod
    def setUpClass(cls):
        cls.src_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), 'data'))
        cls.bckp_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '.data'))
        super(EFSMTest, cls).setUpClass()

    @property
    def test_entry_name(self):
        return 'TestEFSTEntry'

    @property
    def test_entry_name_shortcut(self):
        return self.test_entry_name[1:11]

    @property
    def test_backend_path(self):
      return os.path.join(self.src_dir, 'test_backend')

    @property
    def test_mount_path(self):
      test_mount_path = os.path.join(self.src_dir, 'mnt')
      if not os.path.exists(test_mount_path):
        os.makedirs(test_mount_path)
      return test_mount_path

    @property
    def test_mount_name(self):
      return ''.join((self.test_entry_name, '_Mount'))

    @property
    def test_entry(self, type = EntryTypes.CipherText):
        return ConfigEntries.EFSTEntry(
                    type,
                    'efst-entry-TestEFSTEntry',
                    '{}/test_backend/.encfs6.xml'.format(self.src_dir),
                    '{}/test_backend'.format(self.src_dir),
                    '{}/mnt'.format(self.src_dir),
                    '1',
                    'TestEFSTEntry_Mount')


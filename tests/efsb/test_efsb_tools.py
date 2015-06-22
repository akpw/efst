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

import os
from .test_efsb_base import EFSBTest
from efst.utils.efst_utils import run_cmd, CmdProcessingError
from efst.encfs.encfs_cfg import EncFSCFG
from efst.encfs.encfs_handler import EncFSHandler
from efst.config.efst_config import config_handler, EFSTConfigHandler, EntryTypes


class EFSBTests(EFSBTest):
    def setUp(self):
        super(EFSBTests, self).setUp()

    def tearDown(self):
        # cleanup
        self.resetDataFromBackup(quiet=True)

    def test_show_backend_info(self):
        #return ##
        self._register_test_entry()

        cmd = 'efsb show -en {} -sk'.format(self.test_entry_name_shortcut)
        output = run_cmd(cmd)
        print('\n', output)

        self._unregister_test_entry()

    def test_encode(self):
        #return ##
        self._register_test_entry()

        cmd = 'efsb encode -en {0} -fn {1}'.format(self.test_entry_name_shortcut,
                                                            self._decoded_name_string())
        output = run_cmd(cmd)
        self.assertIn(self._encoded_name_string(), output.split())

        self._unregister_test_entry()

    def test_decode(self):
        #return ##
        self._register_test_entry()

        cmd = 'efsb decode -en {0} -fn {1}'.format(self.test_entry_name_shortcut,
                                                            self._encoded_name_string())
        output = run_cmd(cmd)
        self.assertIn(self._decoded_name_string(), output.split())

        self._unregister_test_entry()


    # Helpers
    @staticmethod
    def _encoded_name_string():
        return 'N95oj-9Z1FmGDrJ0bet,t7HxZu2s'


    @staticmethod
    def _decoded_name_string():
        return  'EFSBTest_TestString'





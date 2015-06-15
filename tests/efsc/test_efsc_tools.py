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
from .test_efsc_base import EFSCTest
from efst.utils.efst_utils import run_cmd, CmdProcessingError
from efst.encfs.encfs_cfg import EncFSCFG
from efst.config.efst_config import config_handler, EFSTConfigHandler


class EFSCTests(EFSCTest):
    def setUp(self):
        super(EFSCTests, self).setUp()

    def tearDown(self):
        # cleanup
        self.resetDataFromBackup(quiet=True)

    def test_create_key(self):
        #return ##
        cmd = 'efsc create-key -cp {0} -ce {1}'.format(self.src_dir, self.default_cfg_entry_name_shortcut)
        self.assertTrue(self.run_expectant_pwd_cmd(cmd))
        self.assertTrue(os.path.exists(os.path.join(self.src_dir, EncFSCFG.DEFAULT_CFG_FNAME)))

    def test_register_entry(self):
        #return ##
        self._unregister_test_entry()

        # register
        test_cfg_entry = self.test_cfg_entry
        cmd = ''.join(('efsc register -ce {}'.format(self.test_cfg_entry_name),
                    ' -ca {}'.format(test_cfg_entry.cipherAlg),
                    ' -ks {}'.format(test_cfg_entry.keySize),
                    ' -bs {}'.format(test_cfg_entry.blockSize),
                    ' -na {}'.format(test_cfg_entry.nameAlg),
                    ' -cn' if test_cfg_entry.chainedNameIV else '',
                    ' -uv' if test_cfg_entry.uniqueIV else '',
                    ' -bh' if test_cfg_entry.blockMACBytes else '',
                    ' -rb {}'.format(test_cfg_entry.blockMACRandBytes),
                    ' -dh' if test_cfg_entry.allowHoles else ''
                    ))
        run_cmd(cmd)

        # confirm the test entry was registered
        config_handler.read_from_disk()
        self.assertTrue(self.test_cfg_entry_name in config_handler.registered_encfs_cfg_entries())

        # try create a new key with the entry
        cmd = 'efsc create-key -cp {0} -ce {1}'.format(self.src_dir, self.test_cfg_entry_name_shortcut)
        self.assertTrue(self.run_expectant_pwd_cmd(cmd))
        self.assertTrue(os.path.exists(os.path.join(self.src_dir, EncFSCFG.DEFAULT_CFG_FNAME)))

        # unregister
        self.assertTrue(
                config_handler.unregister_encfs_cfg_entry(entry_name = self.test_cfg_entry_name, quiet = True))


    def test_show_entry(self):
        #return ##
        self._register_test_entry()

        cmd = 'efsc show -ce {}'.format(self.test_cfg_entry_name_shortcut)
        output = run_cmd(cmd)
        print('\n  ', output)


    def test_unregister_entry(self):
        #return ##
        self._register_test_entry()

        cmd = 'efsc unregister -ce {}'.format(self.test_cfg_entry_name_shortcut)
        output = run_cmd(cmd)

        # confirm the test entry was unregistered
        config_handler.read_from_disk()
        self.assertTrue(self.test_cfg_entry_name not in config_handler.registered_encfs_cfg_entries())


    # Helpers
    def _register_test_entry(self):
        # if not already registered, register
        if not self.test_cfg_entry_name in config_handler.registered_encfs_cfg_entries():
            test_cfg_entry = self.test_cfg_entry_config
            self.assertTrue(
                config_handler.register_encfs_cfg_entry(entry_name = self.test_cfg_entry_name,
                                                            entry_info = test_cfg_entry, quiet = True))

    def _unregister_test_entry(self):
        if self.test_cfg_entry_name in config_handler.registered_encfs_cfg_entries():
            # if already registered, unregister
            self.assertTrue(
                config_handler.unregister_encfs_cfg_entry(entry_name = self.test_cfg_entry_name, quiet = True))



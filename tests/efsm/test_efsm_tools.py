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
from .test_efsm_base import EFSMTest
from efst.utils.efst_utils import run_cmd, CmdProcessingError
from efst.encfs.encfs_cfg import EncFSCFG
from efst.encfs.encfs_handler import EncFSHandler
from efst.config.efst_config import config_handler, EntryTypes, EFSTConfigKeys


class EFSMTests(EFSMTest):
    def setUp(self):
        super(EFSMTests, self).setUp()
        self.assertTrue(os.environ[EncFSCFG.ENCFS_CONFIG] == self.test_encfs_config)

    def tearDown(self):
        # cleanup
        self.resetDataFromBackup(quiet=True)

    def test_create(self):
        #return ##
        self._unregister_test_entry()

        backend_path = os.path.join(self.test_backend_path, 'created')
        cmd = ''.join(('efsm create',
                        ' -en {}'.format(self.test_entry_name),
                        ' -bp {}'.format(backend_path),
                        ' -cp {}'.format(self.src_dir),
                        ' -r',
                        ' -i 1',
                        ' -mp {}'.format(self.test_mount_path),
                        ' -mn {}'.format(self.test_mount_name),
                        ' -ce {}'.format(self.default_cfg_entry_name_shortcut)
                        ))
        self.assertTrue(self.run_expectant_pwd_cmd(cmd, ask_to_store = True))
        self.assertTrue(os.path.exists(backend_path))
        self.assertTrue(os.path.exists(os.path.join(self.src_dir, EncFSCFG.DEFAULT_CFG_FNAME)))

        # unregister
        config_handler.read_from_disk()
        self._unregister_test_entry()

    def test_register(self):
        #return ##
        self._unregister_test_entry()

        cmd = ''.join(('efsm register',
                        ' -en {}'.format(self.test_entry_name),
                        ' -bp {}'.format(self.test_backend_path),
                        ' -cp {}'.format(os.path.join(self.test_backend_path, EncFSCFG.DEFAULT_CFG_FNAME)),
                        ' -r',
                        ' -i 1',
                        ' -mp {}'.format(self.test_mount_path),
                        ' -mn {}'.format(self.test_mount_name)
                        ))
        output = run_cmd(cmd)

        # confirm the test entry was registered
        config_handler.read_from_disk()
        self.assertTrue(self.test_entry_name in config_handler.registered_entries())

        self._unregister_test_entry()

    def test_show(self):
        #return ##
        self._register_test_entry()

        cmd = 'efsm show -en {}'.format(self.test_entry_name_shortcut)
        output = run_cmd(cmd)
        print('\n', output)

        self._unregister_test_entry()

    def test_mount(self):
        #return ##
        self._register_test_entry()

        cmd = 'efsm mount -en {}'.format(self.test_entry_name_shortcut)
        output = run_cmd(cmd)
        self.assertTrue(os.path.exists(self.test_entry.mount_dir_path) \
                                        and os.path.ismount(self.test_entry.mount_dir_path))
        self._umount_test_entry()
        self._unregister_test_entry()

    def test_mount_all(self):
        #return ##
        self._register_test_entry()

        cmd = 'efsm mount -en {}'.format(EFSTConfigKeys.BATCH_MOUNT_ENTRIES_SYMBOL)
        output = run_cmd(cmd)
        self.assertTrue(os.path.exists(self.test_entry.mount_dir_path) \
                                        and os.path.ismount(self.test_entry.mount_dir_path))
        self._umount_test_entry()
        self._unregister_test_entry()

    def test_umount(self):
        #return ##
        self._register_test_entry()
        self._mount_test_entry()

        cmd = 'efsm umount -en {}'.format(self.test_entry_name_shortcut)
        output = run_cmd(cmd)
        self.assertTrue(os.path.exists(self.test_entry.mount_dir_path) \
                                        and not os.path.ismount(self.test_entry.mount_dir_path))
        self._unregister_test_entry()

    def test_umount_all(self):
        #return ##
        self._register_test_entry()
        self._mount_test_entry()

        cmd = 'efsm umount -en {}'.format(EFSTConfigKeys.BATCH_MOUNT_ENTRIES_SYMBOL)
        output = run_cmd(cmd)
        self.assertTrue(os.path.exists(self.test_entry.mount_dir_path) \
                                        and not os.path.ismount(self.test_entry.mount_dir_path))
        self._unregister_test_entry()



    # Helpers
    def _mount_test_entry(self):
       self.assertTrue(EncFSHandler.mount(self.test_password,
                            enc_cfg_path = self.test_entry.encfs_config_path,
                            encfs_dir_path = self.test_entry.encfs_dir_path,
                            mount_dir_path = self.test_entry.mount_dir_path,
                            mount_name = self.test_entry.volume_name,
                            reverse = True if self.test_entry.entry_type == EntryTypes.ReversedCipherText else False,
                            unmount_on_idle = self.test_entry.unmount_on_idle,
                            quiet = True))

    def _umount_test_entry(self):
        self.assertTrue(EncFSHandler.umount(mount_dir_path = self.test_entry.mount_dir_path, quiet = True))

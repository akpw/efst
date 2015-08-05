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

import unittest, os, sys
import shutil, pexpect
from efst.utils.efst_utils import FSHelper
from efst.config.efst_config import config_handler, EFSTConfigHandler, EFSTConfigKeys
from efst.config.efst_config import ConfigEntries, EntryTypes
from efst.encfs.encfs_handler import EncFSHandler

class EFSTTest(unittest.TestCase):
    src_dir = bckp_dir = None

    encfs_config_backup = None
    test_encfs_config = 'A_BOGUS_ENCFS6_CONFIG_VAR'

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.bckp_dir):
            os.makedirs(cls.bckp_dir)
        if not os.path.exists(cls.src_dir):
            os.makedirs(cls.src_dir)
        cls.resetDataFromBackup()
        cls.encfs_config_backup = EncFSHandler._encfs6_config_backup_and_reset(cls.test_encfs_config)

    @classmethod
    def tearDownClass(cls):
        if cls.encfs_config_backup:
            print('will be restoring the ENCFS6_CONFIG env. var to its initial value:\n\t{}'.format(cls.encfs_config_backup))
        EncFSHandler._encfs6_config_restore(cls.encfs_config_backup)

    @classmethod
    def resetDataFromBackup(cls, quiet = False):
        ''' If needed, resets tests data to its original state
        '''
        if cls.src_dir == cls.bckp_dir == None:
            # reset check not required
            return

        # helper functions
        rpath = lambda r,f: os.path.join(os.path.realpath(r),f)

        # check the files
        data_fpaths = [rpath(r,f)
                        for r,d,files in os.walk(cls.src_dir) for f in files]
        bckp_fpaths = [rpath(r,f)
                        for r,d,files in os.walk(cls.bckp_dir) for f in files]
        #  num files
        restore_needed = len(data_fpaths) != len(bckp_fpaths)
        if restore_needed:
            if not quiet:
                print('Need restore on num files mismatch')
        else:
            # file names matches
            restore_needed = set((os.path.basename(f) for f in data_fpaths)) != \
                             set((os.path.basename(f) for f in bckp_fpaths))
            if restore_needed:
                if not quiet:
                    print('Need restore on files names mismatch')

        if not restore_needed:
            # check the dirs
            data_dpaths = [rpath(r,d)
                            for r,dirs,f in os.walk(cls.src_dir) for d in dirs]
            bckp_dpaths = [rpath(r,d)
                            for r,dirs,f in os.walk(cls.bckp_dir) for d in dirs]
            # num dirs
            restore_needed = len(data_dpaths) != len(bckp_dpaths)
            if restore_needed:
                if not quiet:
                    print('Need restore on num dirs mismatch')
            else:
                # dir names matches
                restore_needed = set((os.path.basename(d) for d in data_dpaths)) != \
                                 set((os.path.basename(d) for d in bckp_dpaths))
                if restore_needed:
                    if not quiet:
                        print('Need restore on dir names mismatch')

        if not restore_needed:
           # compare files hashes
            data_fpaths_hashes = {os.path.basename(fpath): FSHelper.file_md5(fpath, hex=True)
                                                        for fpath in data_fpaths}
            bckp_files_hashes = {os.path.basename(fpath): FSHelper.file_md5(fpath, hex=True)
                                                        for fpath in bckp_fpaths}
            restore_needed = set(data_fpaths_hashes.items()) != set(bckp_files_hashes.items())
            if restore_needed:
                if not quiet:
                    print('Need restore on changes in files:')

        if restore_needed:
            # reset everything back to original
            if not quiet:
                print('\nRestoring files...\n')
            shutil.rmtree(cls.src_dir)
            shutil.copytree(cls.bckp_dir, cls.src_dir)
        else:
            if not quiet:
                print('No restore needed')

    @property
    def test_password(self):
        return 'a_bogus_test_pwd'

    def run_expectant_pwd_cmd(self, cmd, ask_to_store = False, store = True):
        ''' Supplies a bogus password for creating keys
        '''

        child = pexpect.spawnu(cmd)

        child.expect('Enter password')
        child.sendline(self.test_password)

        child.expect('Confirm password')
        child.sendline(self.test_password)

        if ask_to_store:
            child.expect('Do you want to securely store the password for later use')
            child.sendline('y' if store else 'n')

        child.expect(pexpect.EOF, timeout=None)
        child.close()

        if child.exitstatus == 0:
            return True

        return False

    @property
    def default_cfg_entry_name(self):
        return EFSTConfigKeys.DEFAULT_CFG_ENTRY_KEY

    @property
    def default_cfg_entry_name_shortcut(self):
        return EFSTConfigKeys.DEFAULT_CFG_ENTRY_KEY[3:11]


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
                    False,
                    'TestEFSTEntry_Mount')

    # Helpers
    def _register_test_entry(self):
        # if not already registered, register
        if not self.test_entry_name in config_handler.registered_entries():
            self.assertTrue(
                config_handler.register_entry(entry_name = self.test_entry_name,
                                              entry_info = self.test_entry, quiet = True))

    def _unregister_test_entry(self):
        if self.test_entry_name in config_handler.registered_entries():
            # if registered, unregister
            self.assertTrue(
                config_handler.unregister_entry(entry_name = self.test_entry_name, quiet = True))

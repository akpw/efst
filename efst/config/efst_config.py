# coding=utf8
## Copyright (c) 2015 Arseniy Kuznetsov
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

import os, sys
from enum import IntEnum
from collections import namedtuple
from configobj import ConfigObj
from pkg_resources import Requirement, resource_filename
from efst.utils.efst_utils import FSHelper
from efst.encfs.encfs_cfg import EncFSCFG


''' EFST conf file handling
'''

class EntryTypes(IntEnum):
    ''' Defines EFST entries types
    '''
    CipherText = 0
    PlainText = 1


class EFSTConfigKeys:
    ''' EFST config file keys
    '''
    # Section Keys
    CIPHER_TEXT_ENTRIES_KEY = 'CipherTextEntries'
    REVERSED_CIPHER_TEXT_ENTRIES_KEY = 'ReversedCipherTextEntries'
    ENCFS_CFG_ENTRIES_KEY = 'EncFSConfigEntries'

    # UnRegistered entries placeholder
    NO_ENTRIES_REGISTERED = 'NoEntriesRegistered'

    # EncFS Entry Keys
    PWD_ENTRY_NAME_KEY = 'PWD_ENTRY_NAME'
    ENCFS6_CONFIG_PATH_KEY = 'ENCFS6_CONFIG_PATH'
    ENCFS_DIR_PATH_KEY = 'ENCFS_DIR_PATH'
    MOUNT_DIR_PATH_KEY = 'MOUNT_DIR_PATH'
    UNMOUNT_ON_IDLE_KEY = 'UNMOUNT_ON_IDLE'
    VOLUME_NAME_KEY = 'VOLUME_NAME'

    # EncFS Config Entry Keys
    DEFAULT_CFG_ENTRY_KEY = 'EFSTConfigDefault'

    CIPHER_ALG = 'cipherAlg'
    KEY_SIZE = 'keySize'
    BLOCK_SIZE = 'blockSize'
    NAME_ALG = 'nameAlg'
    CHANED_NAME_IV = 'chainedNameIV'
    UNIQUE_IV = 'uniqueIV'
    BLOCK_MAC_BYTES = 'blockMACBytes'
    BLOCK_MAC_RAND_BYTES = 'blockMACRandBytes'
    ALLOW_HOLES = 'allowHoles'

    @staticmethod
    def entry_key_for_type(entry_type):
        if entry_type == EntryTypes.CipherText:
            return EFSTConfigKeys.CIPHER_TEXT_ENTRIES_KEY
        else:
            return EFSTConfigKeys.REVERSED_CIPHER_TEXT_ENTRIES_KEY

    @staticmethod
    def entry_type_for_key(entry_key):
        if entry_key == EFSTConfigKeys.CIPHER_TEXT_ENTRIES_KEY:
            return EntryTypes.CipherText
        else:
            return EntryTypes.PlainText


class ConfigEntries:
    EFSTEntry = namedtuple('EFSTEntry',
                        ['entry_type', 'pwd_entry', 'encfs_config_path', 'encfs_dir_path',
                                            'mount_dir_path', 'unmount_on_idle', 'volume_name'])


class OSConfig:
    ''' OS-related config
    '''

    @property
    def mountpoint_folder(self):
        return ''

    @property
    def umount_cmd(self):
        return ''

    @property
    def volname_cmd(self):
        return ''

    @property
    def os_block_size(self):
        ''' Filesystem blocksize
        '''
        return os.stat(self.mountpoint_folder).st_blksize


class OSXConfig(OSConfig):
    ''' OSX-related config
    '''
    @property
    def mountpoint_folder(self):
        return FSHelper.full_path('/Volumes')

    @property
    def umount_cmd(self):
        return 'umount'

    @property
    def volname_cmd(self):
        return '-o volname='


class LinuxConfig(OSConfig):
    ''' Linux-related config
    '''
    @property
    def mountpoint_folder(self):
        return FSHelper.full_path("~/efst/mnt")

    @property
    def umount_cmd(self):
        return 'fusermount -u'


class EFSTConfigHandler:
    def __init__(self, lookup_path = None):
        if lookup_path is None:
            lookup_path = resource_filename(Requirement.parse("efst"), "efst/config/efst.conf")
        self.config = ConfigObj(lookup_path)

        if sys.platform == 'linux':
            self.os_config = LinuxConfig()
        elif sys.platform == 'darwin':
            self.os_config = OSXConfig()

        if not os.path.exists(self.os_config.mountpoint_folder):
            os.makedirs(self.os_config.mountpoint_folder)


    # EFST entries
    ##############
    def register_entry(self, entry_name, entry_type, pwd_entry,
                            conf_path, encfs_dir_path, mount_dir_path,
                            mount_name, unmount_on_idle = 0, quiet = False):
        ''' Registers EFST conf entry
        '''
        entry_key = EFSTConfigKeys.entry_key_for_type(entry_type)

        if entry_name in self.registered_entries():
            if not quiet:
                print('"{0}": entry name already registered as a {1} Entry'.format(entry_name,
                    'Reversed CipherText' if self._entry_key(entry_name) == EFSTConfigKeys.REVERSED_CIPHER_TEXT_ENTRIES_KEY else 'CipherText'))
        else:
            self.config[entry_key][entry_name] = {
                    EFSTConfigKeys.PWD_ENTRY_NAME_KEY: pwd_entry,
                    EFSTConfigKeys.ENCFS6_CONFIG_PATH_KEY: conf_path,
                    EFSTConfigKeys.ENCFS_DIR_PATH_KEY: encfs_dir_path,
                    EFSTConfigKeys.MOUNT_DIR_PATH_KEY: mount_dir_path,
                    EFSTConfigKeys.UNMOUNT_ON_IDLE_KEY: unmount_on_idle,
                    EFSTConfigKeys.VOLUME_NAME_KEY: mount_name }
            self.config.write()
            if not quiet:
                print('{0} Entry registered: {1}'.format(
                            'CipherText' if entry_key == EFSTConfigKeys.CIPHER_TEXT_ENTRIES_KEY
                                                                        else 'Reversed CipherText', entry_name))

    def unregister_entry(self, entry_name, quiet = False):
        ''' Un-registers EFST conf entry
        '''
        entry_key = self._entry_key(entry_name)
        if entry_key:
            del(self.config[entry_key][entry_name])
            self.config.write()
            if not quiet:
                print('Unregistered entry: {}'.format(entry_name))
            return True
        else:
            if not quiet:
                print('Entry is not registered: {}'.format(entry_name))
            return False

    def registered_entries(self):
        ''' All EFST registered entries
        '''
        registered_entries = [entry for entry in self.config[EFSTConfigKeys.CIPHER_TEXT_ENTRIES_KEY].keys()]
        registered_entries += [entry for entry in self.config[EFSTConfigKeys.REVERSED_CIPHER_TEXT_ENTRIES_KEY].keys()]
        if not registered_entries:
            registered_entries = [EFSTConfigKeys.NO_ENTRIES_REGISTERED]
        return registered_entries

    def entry(self, entry_name):
        ''' Given an entry name, reads and returns the entry info
        '''
        entry = None
        entry_key = self._entry_key(entry_name)
        if entry_key:
            entry_reader = self.config[entry_key][entry_name]
            unmount_on_idle = entry_reader.get(EFSTConfigKeys.UNMOUNT_ON_IDLE_KEY)
            unmount_on_idle = int(unmount_on_idle) if unmount_on_idle else 0
            entry = ConfigEntries.EFSTEntry(
                        EFSTConfigKeys.entry_type_for_key(entry_key),
                        entry_reader.get(EFSTConfigKeys.PWD_ENTRY_NAME_KEY),
                        FSHelper.full_path(entry_reader.get(EFSTConfigKeys.ENCFS6_CONFIG_PATH_KEY)),
                        FSHelper.full_path(entry_reader.get(EFSTConfigKeys.ENCFS_DIR_PATH_KEY)),
                        FSHelper.full_path(entry_reader.get(EFSTConfigKeys.MOUNT_DIR_PATH_KEY)),
                        unmount_on_idle,
                        entry_reader.get(EFSTConfigKeys.VOLUME_NAME_KEY))
        return entry

    # EncFS Config entries
    #######################
    def registered_encfs_cfg_entries(self):
        ''' All EncFS registered configurations
        '''
        return [entry for entry in self.config[EFSTConfigKeys.ENCFS_CFG_ENTRIES_KEY].keys()]

    def register_encfs_cfg_entry(self, entry_name, entry_info):
        ''' Registeres EncFS configuration
        '''
        if entry_name in self.registered_encfs_cfg_entries():
            print('"{}": EncFS conf. entry already registered'.format(entry_name))
        else:
            self.config[EFSTConfigKeys.ENCFS_CFG_ENTRIES_KEY][entry_name] = {
                    EFSTConfigKeys.CIPHER_ALG: entry_info.cipherAlg,
                    EFSTConfigKeys.KEY_SIZE: entry_info.keySize,
                    EFSTConfigKeys.BLOCK_SIZE: entry_info.blockSize,
                    EFSTConfigKeys.NAME_ALG: entry_info.nameAlg,
                    EFSTConfigKeys.CHANED_NAME_IV: entry_info.chainedNameIV,
                    EFSTConfigKeys.UNIQUE_IV: entry_info.uniqueIV,
                    EFSTConfigKeys.BLOCK_MAC_BYTES: entry_info.blockMACBytes,
                    EFSTConfigKeys.BLOCK_MAC_RAND_BYTES: entry_info.blockMACRandBytes,
                    EFSTConfigKeys.ALLOW_HOLES: entry_info.allowHoles}
            self.config.write()
            print('{0} entry registered'.format(entry_name))

    def unregister_encfs_cfg_entry(self, entry_name):
        ''' Un-registeres EncFS configuration
        '''
        if not entry_name in self.registered_encfs_cfg_entries():
            print('"{0}": EncFS conf. entry not registered'.format(entry_name))
            return False
        else:
            del(self.config[EFSTConfigKeys.ENCFS_CFG_ENTRIES_KEY][entry_name])
            self.config.write()
            print('Unregistered entry: {}'.format(entry_name))
            return True

    def encfs_cfg_entry(self, cfg_entry_name = None):
        ''' Given an EncFS conf. entry name, reads and returns the entry info
        '''
        entry = None

        if not cfg_entry_name:
            cfg_entry_name = EFSTConfigKeys.DEFAULT_CFG_ENTRY_KEY

        if cfg_entry_name in self.config[EFSTConfigKeys.ENCFS_CFG_ENTRIES_KEY]:
            entry_reader = self.config[EFSTConfigKeys.ENCFS_CFG_ENTRIES_KEY][cfg_entry_name]
            entry = EncFSCFG.EncFSCfgEntry(
                        entry_reader.get(EFSTConfigKeys.CIPHER_ALG),
                        entry_reader.get(EFSTConfigKeys.KEY_SIZE),
                        entry_reader.get(EFSTConfigKeys.BLOCK_SIZE),
                        entry_reader.get(EFSTConfigKeys.NAME_ALG),
                        entry_reader.get(EFSTConfigKeys.CHANED_NAME_IV),
                        entry_reader.get(EFSTConfigKeys.UNIQUE_IV),
                        entry_reader.get(EFSTConfigKeys.BLOCK_MAC_BYTES),
                        entry_reader.get(EFSTConfigKeys.BLOCK_MAC_RAND_BYTES),
                        entry_reader.get(EFSTConfigKeys.ALLOW_HOLES))
        return entry

    # Internal helpers
    def _entry_key(self, entry_name):
        if entry_name in self.config[EFSTConfigKeys.CIPHER_TEXT_ENTRIES_KEY]:
            return EFSTConfigKeys.CIPHER_TEXT_ENTRIES_KEY
        elif entry_name in self.config[EFSTConfigKeys.REVERSED_CIPHER_TEXT_ENTRIES_KEY]:
            return EFSTConfigKeys.REVERSED_CIPHER_TEXT_ENTRIES_KEY
        else:
            return None

# Simplest possible Singleton impl
config_handler = EFSTConfigHandler()

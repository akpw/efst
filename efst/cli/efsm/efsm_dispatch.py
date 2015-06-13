#!/usr/bin/env python
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

import os
from efst.cli.efst.efst_dispatch import EFSTDispatcher
from efst.encfs.encfs_handler import EncFSHandler
from efst.config.efst_config import config_handler, EntryTypes, EFSTConfigKeys
from efst.cli.efsm.efsm_options import EFSMOptionsParser, EFSMCommands
from efst.utils.efst_utils import PasswordHandler


class EFSMDispatcher(EFSTDispatcher):
    ''' EFSM Commands Dispatcher
    '''
    def __init__(self):
        self.option_parser = EFSMOptionsParser()

    # Dispatcher
    def dispatch(self):
        if not super().dispatch():
            args = self.option_parser.parse_options()

            if args['sub_cmd'] in (EFSMCommands.CREATE):
                if args['reverse']:
                    self.create_entry(args, EntryTypes.PlainText)
                else:
                    self.create_entry(args, EntryTypes.CipherText)

            elif args['sub_cmd'] in (EFSMCommands.REGISTER):
                if args['reverse']:
                    self.register_entry(args, EntryTypes.PlainText)
                else:
                    self.register_entry(args, EntryTypes.CipherText)

            elif args['sub_cmd'] == EFSMCommands.SHOW:
                self.show_entry(args)

            elif args['sub_cmd'] == EFSMCommands.UNREGISTER:
                self.unregister_entry(args)

            elif args['sub_cmd'] == EFSMCommands.MOUNT:
                self.mount_entry(args)

            elif args['sub_cmd'] == EFSMCommands.UMOUNT:
                self.umount_entry(args)

            else:
                print('Nothing to dispatch')
                return False

        return True


    # Dispatched methods
    def create_entry(self, args, entry_type):
        ''' Creates and registers EncFS backend store / respective view
        '''

        if not os.path.exists(args['backend_path']):
            os.makedirs(args['backend_path'])

        pwd, result = self.create_key(args)

        if result:
            # offer to store the password
            self._store_pwd(pwd, args['pwd_entry'])

            # register entry
            self.register_entry(args, entry_type)


    def register_entry(self, args, entry_type):
        ''' Registers EncFS backend store / respective view
        '''
        config_handler.register_entry(entry_name = args['entry_name'],
                                                        entry_type = entry_type,
                                                        pwd_entry = args['pwd_entry'],
                                                        conf_path = args['conf_path'],
                                                        encfs_dir_path = args['backend_path'],
                                                        mount_dir_path = args['mountpoint_path'],
                                                        mount_name = args['mount_name'],
                                                        unmount_on_idle = args['idle_minutes'])

    def show_entry(self, args):
        et_desc = lambda type: 'Reversed CipherText' if type == EntryTypes.PlainText else 'CipherText'
        mp_desc = lambda type: 'CipherText' if type == EntryTypes.PlainText else 'Plaintext'
        be_desc = lambda type: 'Plaintext' if type == EntryTypes.PlainText else 'CipherText'

        umount_idle_desc = lambda idle: '{} mins'.format(idle) if idle else 'Disabled'

        entry = config_handler.entry(args['entry_name'])
        print('Entry name: {}'.format(args['entry_name']))
        print('  Entry type: {}'.format(et_desc(entry.entry_type)))
        print('  Password store entry: {}'.format(entry.pwd_entry))
        print('  Conf/Key file: {}'.format(entry.encfs_config_path))
        print('  Back-end store folder ({0}): {1}'.format(be_desc(entry.entry_type), entry.encfs_dir_path))
        print('  Mount folder ({0}): {1}'.format(mp_desc(entry.entry_type), entry.mount_dir_path))
        print('  Un-mount on idle: {}'.format(umount_idle_desc(entry.unmount_on_idle)))
        print('  Volume name: {}'.format(entry.volume_name))

    def unregister_entry(self, args):
        ''' Un-Registers EncFS entry
        '''
        entry = config_handler.entry(args['entry_name'])

        # if mounted, unmount
        self.umount_entry(args, quiet = True)

        if config_handler.unregister_entry(args['entry_name']):
            # remove pwd entry as well
            PasswordHandler.delete_pwd(entry.pwd_entry)

    def mount_entry(self, args):
        ''' Mounts a registered EncFS entry
        '''
        print(args['entry_name'])
        mount_entry = config_handler.entry(args['entry_name'])

        pwd, new_pwd = PasswordHandler.get_pwd(mount_entry.pwd_entry)
        if not pwd:
            print('No password entered, exiting')
        else:
            if EncFSHandler.mount(pwd,
                        mount_entry.encfs_config_path,
                        mount_entry.encfs_dir_path,
                        mount_entry.mount_dir_path,
                        mount_entry.volume_name,
                        unmount_on_idle = mount_entry.unmount_on_idle,
                        reverse = True if mount_entry.entry_type == EntryTypes.PlainText else False):
                if new_pwd:
                    self._store_pwd(pwd, mount_entry.pwd_entry)

    def umount_entry(self, args, quiet = False):
        ''' Un-mounts a registered EncFS entry
        '''
        umount_entry = config_handler.entry(args['entry_name'])
        EncFSHandler.umount(umount_entry.mount_dir_path, quiet = quiet)


def main():
    EFSMDispatcher().dispatch()

if __name__ == '__main__':
    main()

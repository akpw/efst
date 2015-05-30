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
from efst.encfs.encfs_handler import EncFSHandler
from efst.config.efst_config import config_handler, EntryTypes
from efst.cli.efst.efst_dispatch import EFSTDispatcher
from efst.cli.efsm.efsm_options import EFSMOptionsParser
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

            if args['sub_cmd'] in ('create'):
                if args['reverse']:
                    self.create_entry(args, EntryTypes.PlainText)
                else:
                    self.create_entry(args, EntryTypes.CipherText)

            elif args['sub_cmd'] in ('register'):
                if args['reverse']:
                    self.register_entry(args, EntryTypes.PlainText)
                else:
                    self.register_entry(args, EntryTypes.CipherText)

            elif args['sub_cmd'] == 'unregister':
                self.unregister_entry(args)

            elif args['sub_cmd'] == 'mount':
                self.mount_entry(args)

            elif args['sub_cmd'] == 'umount':
                self.umount_entry(args)

    # Dispatched methods
    def create_entry(self, args, entry_type):
        ''' Creates and registeres backend store / respective view
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
        config_handler.register_entry(entry_name = args['entry_name'],
                                                        entry_type = entry_type,
                                                        pwd_entry = args['pwd_entry'],
                                                        conf_path = args['conf_path'],
                                                        encfs_dir_path = args['backend_path'],
                                                        mount_dir_path = args['mountpoint_path'],
                                                        mount_name = args['mount_name'])

    def unregister_entry(self, args):
        entry = config_handler.entry(args['entry_name'])

        # if mounted, unmount
        self.umount_entry(args, quiet = True)

        if config_handler.unregister_entry(args['entry_name']):
            # remove pwd entry as well
            PasswordHandler.delete_pwd(entry.pwd_entry)

    def mount_entry(self, args):
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
                        reverse = True if mount_entry.entry_type == EntryTypes.PlainText else False):
                if new_pwd:
                    self._store_pwd(pwd, mount_entry.pwd_entry)

    def umount_entry(self, args, quiet = False):
        umount_entry = config_handler.entry(args['entry_name'])
        EncFSHandler.umount(umount_entry.mount_dir_path, quiet = quiet)


def main():
    EFSMDispatcher().dispatch()

if __name__ == '__main__':
    main()
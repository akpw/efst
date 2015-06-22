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

from efst.cli.efst.efst_dispatch import EFSTDispatcher
from efst.encfs.encfs_handler import EncFSHandler
from efst.cli.efsb.efsb_options import EFSBOptionsParser, EFSBCommands
from efst.config.efst_config import config_handler, EntryTypes
from efst.utils.efst_utils import PasswordHandler
from efst.encfs.encfs_cfg import EncFSCipherAlg, EncFSNameAlg, EncFSCFG


class EFSBDispatcher(EFSTDispatcher):
    ''' EFSB Commands Dispatcher
    '''
    def __init__(self):
        self.option_parser = EFSBOptionsParser()

    # Dispatcher
    def dispatch(self):
        if not super().dispatch():
            args = self.option_parser.parse_options()

            if args['sub_cmd'] == EFSBCommands.SHOW:
                self.show_info(args)
            elif args['sub_cmd'] == EFSBCommands.ENCODE:
                self.encode(args)
            elif args['sub_cmd'] == EFSBCommands.DECODE:
                self.decode(args)
            else:
                print('Nothing to dispatch')
                return False

        return True

    # Dispatched methods
    def show_info(self, args):
        entry = config_handler.entry(args['entry_name'])
        if entry:
            if entry.entry_type == EntryTypes.CipherText:
                entry_type = 'CipherText'
            else:
                entry_type = 'Reversed CipherText'
            # Print backend info for a given key
            print('{} Volume Info:'.format(entry_type))

            print('  Backend Store Path ({0}):\n\t{1}'.format(entry_type, entry.encfs_dir_path))
            print('  Conf/Key Path:\n\t{}'.format(entry.encfs_config_path))

            if args['show_key']:
                pwd, new_pwd = PasswordHandler.get_pwd(entry.pwd_entry)
                if not pwd:
                    print('Password is required to show the encription key value')
                else:
                    key_info = EncFSHandler.key_info(encfs_dir_path = entry.encfs_dir_path, pwd = pwd,
                                                                    enc_cfg_path = entry.encfs_config_path)
                    if key_info:
                        if new_pwd:
                            self._store_pwd(pwd, entry.pwd_entry)

                        # Print the key
                        print('  The Key (PlainText Value):\n\t{}'.format(key_info))

            backend_info = EncFSHandler.backend_info(encfs_dir_path = entry.encfs_dir_path,
                                                                enc_cfg_path = entry.encfs_config_path)
            if backend_info:
                print('  General Info:')
                for line in backend_info.splitlines():
                    if line:
                        print('\t{}'.format(line))

            if args['show_cruft']:
                print('  Un-decodable filenames:')
                print('\tTDB...')

    def encode(self, args):
        entry = config_handler.entry(args['entry_name'])
        if entry:
            pwd, new_pwd = PasswordHandler.get_pwd(entry.pwd_entry)
            encoded = EncFSHandler.encode(encfs_dir_path = entry.encfs_dir_path,
                                                        enc_cfg_path = entry.encfs_config_path,
                                                                filename = args['file_entry_name'], pwd = pwd)
            if encoded:
                if new_pwd:
                    self._store_pwd(pwd, entry.pwd_entry)

                # Print the encoded name
                print('Encoded: {}'.format(encoded))


    def decode(self, args):
        entry = config_handler.entry(args['entry_name'])
        if entry:
            pwd, new_pwd = PasswordHandler.get_pwd(entry.pwd_entry)
            decoded = EncFSHandler.decode(encfs_dir_path = entry.encfs_dir_path,
                                                        enc_cfg_path = entry.encfs_config_path,
                                                                filename = args['file_entry_name'], pwd = pwd)
            if decoded:
                if new_pwd:
                    self._store_pwd(pwd, entry.pwd_entry)

                # Print the decoded name
                print('Decoded: {}'.format(decoded))


def main():
    EFSBDispatcher().dispatch()

if __name__ == '__main__':
    main()


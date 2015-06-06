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
from efst.cli.efsc.efsc_options import EFSCOptionsParser, EFSCCommands
from efst.config.efst_config import config_handler
from efst.encfs.encfs_cfg import EncFSCipherAlg, EncFSNameAlg, EncFSCFG


class EFSCDispatcher(EFSTDispatcher):
    ''' EFSC Commands Dispatcher
    '''
    def __init__(self):
        self.option_parser = EFSCOptionsParser()

    # Dispatcher
    def dispatch(self):
        if not super().dispatch():
            args = self.option_parser.parse_options()

            if args['sub_cmd'] == EFSCCommands.CREATE_KEY:
                self.create_key(args)

            elif args['sub_cmd'] == EFSCCommands.SHOW:
                self.show_cfg_entry(args)

            elif args['sub_cmd'] == EFSCCommands.REGISTER:
                self.register_cfg_entry(args)

            elif args['sub_cmd'] == EFSCCommands.UNREGISTER:
                self.unregister_cfg_entry(args)

            else:
                print('Nothing to dispatch')
                return False

        return True

    # Dispatched methods
    def show_cfg_entry(self, args):
        entry = config_handler.encfs_cfg_entry(args['entry_name'])
        enable_tr = lambda letter: 'Enabled' if letter.lower() == 'y' else 'Disabled'
        print('Entry name: {}'.format(args['entry_name']))
        print('\tCipher Algorithm: {}'.format(EncFSCipherAlg.alg_name_by_type(entry.cipherAlg)))
        print('\tKey Size: {}'.format(entry.keySize))
        print('\tBlock Size: {}'.format(entry.blockSize))
        print('\tNaming Algorithm: {}'.format(EncFSNameAlg.alg_name_by_type(entry.nameAlg)))
        print('\tFilename initialization vector: {}'.format(enable_tr(entry.chainedNameIV)))
        print('\tPer-file initialization vector: {}'.format(enable_tr(entry.uniqueIV)))
        print('\tBlock authentication code headers: {}'.format(enable_tr(entry.blockMACBytes)))
        print('\tAdd random bytes to each block header: {}'.format(entry.blockMACRandBytes))
        print('\tFile-hole pass-through: {}'.format(enable_tr(entry.allowHoles)))

    def register_cfg_entry(self, args):
        entry_tr = lambda bool_value: 'y' if bool_value else 'n'
        entry_conf = EncFSCFG.EncFSCfgEntry(
                    args['cipher_algorithm'].value,
                    args['key_size'],
                    args['block_size'],
                    args['filename_algorithm'].value,
                    entry_tr(args['chainedNameIV']),
                    entry_tr(args['uniqueIV']),
                    entry_tr(args['blockMACBytes']),
                    args['blockMACRandBytes'],
                    entry_tr(not args['disable_holes']))

        config_handler.register_encfs_cfg_entry(args['entry_name'], entry_conf)


    def unregister_cfg_entry(self, args):
        config_handler.unregister_encfs_cfg_entry(args['entry_name'])



def main():
    EFSCDispatcher().dispatch()

if __name__ == '__main__':
    main()


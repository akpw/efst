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
from efst.config.efst_config import config_handler
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
                self.show_backend_info(args)
            else:
                print('Nothing to dispatch')
                return False

        return True

    # Dispatched methods
    def show_backend_info (self, args):
        entry = config_handler.entry(args['entry_name'])
        if entry:
            backend_info = EncFSHandler.backend_info(encfs_dir_path = entry.encfs_dir_path,
                                                                enc_cfg_path = entry.encfs_config_path)
            if backend_info:
                # Print backend info for a given key
                print('EncFS Backend Store: {}'.format(entry.encfs_dir_path))
                print('EncFS Conf/Key: {}'.format(entry.encfs_config_path))
                for line in backend_info.splitlines():
                    if line:
                        print('  {}'.format(line))

def main():
    EFSBDispatcher().dispatch()

if __name__ == '__main__':
    main()


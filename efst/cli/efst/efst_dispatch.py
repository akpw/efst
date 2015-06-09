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

import efst.cli.efst.checks.chk_pv
import efst.cli.efst.checks.chk_encfs
import sys
from distutils.util import strtobool
from efst.utils.efst_utils import PasswordHandler
from efst.encfs.encfs_handler import EncFSHandler
from efst.config.efst_config import config_handler
from efst.cli.efst.efst_options import EFSTOptionsParser, EFSTCommands
import pkg_resources


class EFSTDispatcher:
    ''' Base EFST Commands Dispatcher
    '''
    def __init__(self):
        self.option_parser = EFSTOptionsParser()

    # Dispatcher
    def dispatch(self):
        args = self.option_parser.parse_options()

        if args['sub_cmd'] == EFSTCommands.VERSION:
            self.print_version()

        elif args['sub_cmd'] == EFSTCommands.INFO:
            self.print_info()

        else:
            # nothing to dispatch
            return False

        return True

    # Dispatched methods
    def print_version(self):
        ''' Prints EFST version info
        '''
        version = pkg_resources.require("efst")[0].version
        print('Encrypted File System Tools version {}'.format(version))

    def print_info(self):
        ''' Prints EFST general info
        '''
        print('Encrypted File System Tools: {}'.format(self.option_parser.script_name))
        print(self.option_parser.description)

    def create_key(self, args):
        ''' Creates EncFS conf/key file at specified location
        '''
        cfg_entry = config_handler.encfs_cfg_entry(args['config_entry'])
        pwd = PasswordHandler.get_pwd_input(confirm = True)
        if not pwd:
            print('No password entered, exiting...')
            sys.exit(0)

        return pwd, EncFSHandler.create_cfg_file(pwd, cfg_entry, args['conf_path'])

    # Internal helpers
    def _store_pwd(self, pwd, pwd_entry):
        answer = input('Do you want to securely store the password for later use? [y/n]: ')
        try:
            answer = strtobool(answer)
        except ValueError:
            print('Not confirmative, the password was not stored')
        if answer:
            PasswordHandler.store_pwd(pwd,pwd_entry)

def main():
    EFSTDispatcher().dispatch()

if __name__ == '__main__':
    main()


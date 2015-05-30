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
from efst.cli.efst.efst_options import EFSTOptionsParser, EFSTHelpFormatter, EFSTCommands
from efst.encfs.encfs_handler import EncFSHandler


class EFSCCommands(EFSTCommands):
    CREATE_KEY = 'create-key'

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        '{}, '.format(cls.CREATE_KEY),
                        '{}, '.format(cls.INFO),
                        '{}'.format(cls.VERSION),
                        '}'))


class EFSCOptionsParser(EFSTOptionsParser):
    ''' EFSC Options Parser
    '''
    def __init__(self):
        self._script_name = 'EFSM'
        self._description = \
    '''
    EFSC is a part of EFST tools. It enables creating
    EncFS conf/key files and managing related EncFS presetes.
    '''

    # Options parsing
    def parse_commands(self, parser):
        ''' Commands parsing
        '''
        subparsers = parser.add_subparsers(dest = 'sub_cmd', title = 'EFSC commands',
                                                                            metavar = EFSCCommands.commands_meta())
        self._add_version(subparsers)

        # Create Key
        create_key_parser = subparsers.add_parser(EFSCCommands.CREATE_KEY,
                                   description = 'Creates EncFS Conf/Key file',
                                   formatter_class=EFSTHelpFormatter)
        required_args_group = create_key_parser.add_argument_group('Required Arguments')
        required_args_group.add_argument('-cp', '--conf-path', dest = 'conf_path',
                        type = str,
                        required = True,
                        help = 'Target path to the EncFS conf/key file')
        self._add_config_entry(create_key_parser)

    # Options checking
    def _check_cmd_args(self, args, parser):
        ''' Validation of supplied CLI commands
        '''
        super()._check_cmd_args(args, parser)
        if args['sub_cmd'] == EFSCCommands.CREATE_KEY:
            if os.path.exists(args['conf_path']):
                # if target path is directory, compile default file name
                if os.path.isdir(args['conf_path']):
                    args['conf_path'] = os.path.join(args['conf_path'], EncFSHandler.DEFAULT_CFG_FNAME)
                else:
                    print('EncFS conf/key file already exists: \n\t"{}"'.format(args['conf_path']))
                    parser.exit()

    @property
    def _default_command(self):
        ''' Default to showing help
        '''
        return None


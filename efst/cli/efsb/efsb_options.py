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
from efst.encfs.encfs_cfg import EncFSCFG
from efst.encfs.encfs_cfg import EncFSCipherAlg, EncFSNameAlg
from efst.config.efst_config import config_handler
from efst.utils.efst_utils import UniquePartialMatchList

class EFSBCommands(EFSTCommands):

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        '{}, '.format(cls.UNREGISTER),
                        '{}'.format(cls.SHOW),
                        '}'))


class EFSBOptionsParser(EFSTOptionsParser):
    ''' EFSB Options Parser
    '''
    def __init__(self):
        self._script_name = 'EFSB'
        self._description = \
    '''
        A part of EFST tools, EFSB is a
        configuration utility for managing EncFS
        back-end stores folders. It can show info
        about registered EFST File Systems, change
        EncFS passwords, list encrypted files,
        encode / decode file names,
        show EncFS cruft info, etc.
    '''

    # Options parsing
    def parse_commands(self, parser):
        ''' Commands parsing
        '''
        subparsers = parser.add_subparsers(dest = 'sub_cmd', title = 'EFSB commands',
                                                                            metavar = EFSBCommands.commands_meta())
        self._add_version(subparsers)
        self._add_info(subparsers)

        # Show
        show_parser = subparsers.add_parser(EFSBCommands.SHOW,
                                   description = 'Shows info about a registered EncFS entry backend store',
                                             formatter_class=EFSTHelpFormatter)
        required_args_group = show_parser.add_argument_group('Required Arguments')
        self._add_entry_name(required_args_group, registered_only = True, help = "Name of a registered EFST entry")


    # Options checking
    def _check_cmd_args(self, args, parser):
        ''' Validation of supplied CLI commands
        '''
        super()._check_cmd_args(args, parser)

        # Registered Entry name could be a partial match, need to expand
        args['entry_name'] = UniquePartialMatchList(
                                    config_handler.registered_entries()).find(args['entry_name'])

    @property
    def _default_command(self):
        ''' Default to showing help
        '''
        return None

    # Helpers

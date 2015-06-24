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
from efst.utils.efst_utils import UniquePartialMatchList, FSHelper

class EFSBCommands(EFSTCommands):
    ENCODE = 'encode'
    DECODE = 'decode'

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        '{},'.format(cls.SHOW),
                        ' {},'.format(cls.ENCODE),
                        ' {}'.format(cls.DECODE),
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
        back-end stores folders. It can show
        registered EFST File Systems info, change
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

        advanced_args_group = show_parser.add_argument_group('Advanced Arguments')
        advanced_args_group.add_argument("-sk", "--show-key", dest='show_key',
                    help = 'Shows encryption key',
                    action='store_true')
        advanced_args_group.add_argument("-cs", "--cruft-summary", dest='cruft_summary',
                    help = 'Shows summary info on un-decodable filenames',
                    action='store_true')
        advanced_args_group.add_argument("-cf", "--cruft-file", dest='cruft_file',
                    type = lambda fpath: FSHelper.full_path(fpath, check_parent_path = True),
                    help = 'Stores detailed cruft info into a file at specified path')

        # Decode
        decode_parser = subparsers.add_parser(EFSBCommands.DECODE,
                                   description = 'Decodes a file entry name to its PlainText version',
                                             formatter_class=EFSTHelpFormatter)
        required_args_group = decode_parser.add_argument_group('Required Arguments')
        self._add_entry_name(required_args_group, registered_only = True, help = "Name of a registered EFST entry")
        self._add_file_entry_name(required_args_group, help = '(File entry) name to decode')

        # Encode
        encode_parser = subparsers.add_parser(EFSBCommands.ENCODE,
                                   description = 'Encodes a file entry name to its CipherText version',
                                             formatter_class=EFSTHelpFormatter)
        required_args_group = encode_parser.add_argument_group('Required Arguments')
        self._add_entry_name(required_args_group, registered_only = True, help = "Name of a registered EFST entry")
        self._add_file_entry_name(required_args_group, help = '(File entry) name to encode')


    # Options checking
    def _check_cmd_args(self, args, parser):
        ''' Validation of supplied CLI commands
        '''
        super()._check_cmd_args(args, parser)

        # Registered Entry name could be a partial match, need to expand
        if args['sub_cmd'] in (EFSBCommands.SHOW, EFSBCommands.ENCODE, EFSBCommands.DECODE):
            args['entry_name'] = UniquePartialMatchList(
                                    config_handler.registered_entries()).find(args['entry_name'])

    @property
    def _default_command(self):
        ''' Default to showing help
        '''
        return None

    # Helpers
    @staticmethod
    def _add_file_entry_name(parser, help = 'Name of file entry'):
        parser.add_argument('-fn', '--file-entry-name', dest = 'file_entry_name',
                        type = str,
                        required = True,
                        help = help)

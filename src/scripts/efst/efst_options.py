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
from argparse import ArgumentParser
from src.config.efst_config import config_handler
from src.utils.efst_utils import FSHelper, UniquePartialMatchList, CustomFormatter
from src.config.efst_config import EFSTConfigKeys

class EFSTOptionsParser:
    ''' Base EFST Options Parser
    '''

    # Internal helpers
    @staticmethod
    def _is_valid_dir_path(parser, path_arg):
        ''' Checks if path_arg is a valid dir path
        '''
        path_arg = FSHelper.full_path(path_arg)
        if not (os.path.exists(path_arg) and os.path.isdir(path_arg)):
            parser.error('"{}" does not seem to be an existing directory path'.format(path_arg))
        else:
            return path_arg

    @staticmethod
    def _is_valid_file_path(parser, path_arg):
        ''' Checks if path_arg is a valid file path
        '''
        path_arg = FSHelper.full_path(path_arg)
        if not (os.path.exists(path_arg) and os.path.isfile(path_arg)):
            parser.error('"{}" does not seem to be an existing file path'.format(path_arg))
        else:
            return path_arg

    @classmethod
    def _add_config_entry(cls, parser):
        ''' Preset config-entry argument
        '''
        advanced_args_group = parser.add_argument_group('Advanced Arguments')
        advanced_args_group.add_argument('-ce', '--config-entry', dest = 'config_entry',
                        type = str,
                        default = EFSTConfigKeys.DEFAULT_CFG_ENTRY_KEY,
                        choices = UniquePartialMatchList(
                                        config_handler.registered_encfs_cfg_entries()),
                        help = 'A preset configuration for creating EncFS configuration/key file')

    @classmethod
    def _add_version(cls, parser):
        ''' Adds the version command
        '''
        parser.add_parser('version', description = 'Displays EFST version info',
                                                        formatter_class=CustomFormatter)

    # Options parsing
    @classmethod
    def parse_global_options(cls, parser):
        ''' Parses global options
        '''
        pass

    @classmethod
    def parse_commands(cls, parser):
        ''' Commands parsing
        '''
        subparsers = parser.add_subparsers(dest = 'sub_cmd', title = 'EFST commands')
        cls._add_version(subparsers)

    # Options checking
    @classmethod
    def _check_args(cls, args, parser):
        ''' Validation of supplied CLI arguments
        '''
        # check if there is a cmd to execute
        cls._check_cmd_args(args, parser)

    @classmethod
    def _check_cmd_args(cls, args, parser):
        ''' Validation of supplied CLI commands
        '''
        # base command check
        if 'sub_cmd' not in args or not args['sub_cmd']:
            # If no command was specified, check for the default one
            if not cls._default_command(args, parser):
                # no appropriate default either
                parser.print_help()
                parser.exit()

    @classmethod
    def _default_command(cls, args, parser):
        ''' If no command was specified, can add a default one
        '''
        return False

    # Parsing Workflow
    @classmethod
    def parse_options(cls, script_name = 'efst',
                                     description = '''
                                            EFST helps secure your data with Encrypted Filesystem (EncFS).
                                            EFST currently provides two main tools, EFS Mounter and EFS Config.
                                            For more information, run "efsm -h" and "efsc -h"
                                          '''):
        ''' General Options parsing workflow
        '''
        parser = ArgumentParser(prog = script_name, description = description)

        cls.parse_global_options(parser)

        cls.parse_commands(parser)

        args = vars(parser.parse_args())

        cls._check_args(args, parser)

        return args

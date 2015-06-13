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
from argparse import ArgumentParser, HelpFormatter
from efst.config.efst_config import config_handler
from efst.utils.efst_utils import FSHelper, UniquePartialMatchList
from efst.config.efst_config import EFSTConfigKeys


class EFSTCommands:
    VERSION = 'version'
    INFO = 'info'
    SHOW = 'show'
    REGISTER = 'register'
    UNREGISTER = 'unregister'

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        '{}, '.format(cls.INFO),
                        '{}'.format(cls.VERSION),
                        '}'))

class EFSTOptionsParser:
    ''' Base EFST Options Parser
    '''
    def __init__(self):
        self._script_name = 'EFST'
        self._description = \
    '''
    Encrypted File System tools help manage
    EncFS-encrypted data, making it easy to organize
    various EncFS assets and then effectively operate it
    via a few simple commands.

    For more information on provided tools, run:
        $ efsm -h
        $ efsc -h
    '''

    @property
    def description(self):
        return self._description

    @property
    def script_name(self):
        return self._script_name

    # Options Parsing Workflow
    def parse_options(self):
        ''' General Options parsing workflow
        '''
        parser = ArgumentParser(prog = self._script_name,
                                    description = self._description,
                                        formatter_class=EFSTHelpFormatter)

        self.parse_global_options(parser)
        self.parse_commands(parser)
        args = vars(parser.parse_args())

        self._check_args(args, parser)

        return args

    def parse_global_options(self, parser):
        ''' Parses global options
        '''
        pass

    def parse_commands(self, parser):
        ''' Commands parsing
        '''
        subparsers = parser.add_subparsers(dest = 'sub_cmd',
                                                title = 'EFST commands',
                                                    metavar = EFSTCommands.commands_meta())
        self._add_version(subparsers)
        self._add_info(subparsers)

    # Options checking
    def _check_args(self, args, parser):
        ''' Validation of supplied CLI arguments
        '''
        # check if there is a cmd to execute
        self._check_cmd_args(args, parser)

    def _check_cmd_args(self, args, parser):
        ''' Validation of supplied CLI commands
        '''
        # base command check
        if 'sub_cmd' not in args or not args['sub_cmd']:
            # If no command was specified, check for the default one
            cmd = self._default_command
            if cmd:
                args['sub_cmd'] = cmd
            else:
                # no appropriate default either
                parser.print_help()
                parser.exit()

    @property
    def _default_command(self):
        ''' If no command was specified, print INFO by default
        '''
        return EFSTCommands.INFO


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

    @staticmethod
    def _add_config_entry(parser):
        ''' Preset config-entry argument
        '''
        advanced_args_group = parser.add_argument_group('Advanced Arguments')
        advanced_args_group.add_argument('-ce', '--config-entry', dest = 'config_entry',
                        type = str,
                        default = EFSTConfigKeys.DEFAULT_CFG_ENTRY_KEY,
                        choices = UniquePartialMatchList(
                                        config_handler.registered_encfs_cfg_entries()),
                        help = 'A registered EFST config entry for creating EncFS config/key files')

    @staticmethod
    def _add_version(parser):
        ''' Adds the version command
        '''
        parser.add_parser(EFSTCommands.VERSION,
                                description = 'Displays EFST version info',
                                        formatter_class=EFSTHelpFormatter)

    @staticmethod
    def _add_info(parser):
        ''' Adds the info command
        '''
        parser.add_parser(EFSTCommands.INFO,
                                description = 'Displays EFST info',
                                        formatter_class=EFSTHelpFormatter)


class EFSTHelpFormatter(HelpFormatter):
    ''' Custom formatter for ArgumentParser
        Disables double metavar display, showing only for long-named options
    '''
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    #parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)



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
from enum import IntEnum
from efst.cli.efst.efst_options import EFSTOptionsParser, EFSTHelpFormatter, EFSTCommands
from efst.encfs.encfs_handler import EncFSHandler
from efst.config.efst_config import config_handler, OSConfig
from efst.utils.efst_utils import FSHelper, UniqueDirNamesChecker, UniquePartialMatchList


class ConfKeyActionType(IntEnum):
    ''' Defines EFS entries types
    '''
    Create = 0
    Register = 1

class EFSMOptionsParser(EFSTOptionsParser):
    ''' EFSM Options Parser
    '''
    @staticmethod
    def _add_entry_name(parser, registered_only = False, help = 'EFSM Entry name'):
        parser.add_argument('-en', '--entry-name', dest = 'entry_name',
                        type = str,
                        metavar = config_handler.registered_entries() if registered_only else None,
                        required = True,
                        choices = UniquePartialMatchList(
                                        config_handler.registered_entries()) if registered_only else None,
                        help = help)

    @classmethod
    def _add_entry_groups(cls, parser, action_type = ConfKeyActionType.Register):
        required_args_group = parser.add_argument_group('Required Arguments')
        cls._add_entry_name(required_args_group)

        # Backend store
        required_args_group.add_argument('-bp', '--backend-path', dest = 'backend_path',
            type = lambda f:FSHelper.full_path(f) \
                    if action_type == ConfKeyActionType.Create \
                        else (lambda d: cls._is_valid_dir_path(parser, d)),
            required = True,
            help = 'Path to the back-end store folder. ' \
                'The backend folder typically contains your ciphered data, for which a plaintext view folder is set up and registered.' \
                'That can reversed via using "--reverse" switch, which results in an on-demand ciphered view for your plaintext back-end data')

        optional_args_group = parser.add_argument_group('Additional Arguments')
        optional_args_group.add_argument('-cp', '--conf-path', dest = 'conf_path',
                        type = lambda f:FSHelper.full_path(f, check_parent_path = True) \
                                 if action_type == ConfKeyActionType.Create \
                                    else (lambda f: cls._is_valid_file_path(parser, f)),
                        help = '{0}ath to the EncFS conf/key file. ' \
                            'If ommitted, a default one will be {1} in the back-end folder'.format(
                                   'P' if action_type == ConfKeyActionType.Register else 'Target p',
                                   'looked up for' if action_type == ConfKeyActionType.Register else 'created'))
        optional_args_group.add_argument("-r", "--reverse", dest='reverse',
                    help = "Enables reverse mode, i.e. a ciphered view for a plaintext back-end data",
                    action='store_true')
        optional_args_group.add_argument('-mp', '--mountpoint-path', dest = 'mountpoint_path',
            type = lambda d: cls._is_valid_dir_path(parser, d),
            help = 'Path to the mountpoint folder. If omitted, will be auto-generated from ' \
                                        'entry name and put in the "{}" folder'.format(OSConfig.MOUNTPOINT_FOLDER))
        optional_args_group.add_argument('-mn', '--mount-name', dest = 'mount_name',
                        type = str,
                        help = 'Mounted volume name. If ommitted, the entry name will be used')


    # Options checking
    @classmethod
    def _check_cmd_args(cls, args, parser):
        ''' Validation of supplied CLI commands
        '''
        super()._check_cmd_args(args, parser)
        if args['sub_cmd'] == 'version':
            # not much to check there
           pass

        elif args['sub_cmd'] not in ('register', 'create'):
            # Registered Entry name could be a partial match, need to expand
            args['entry_name'] = UniquePartialMatchList(
                                        config_handler.registered_entries()).find(args['entry_name'])

        elif args['sub_cmd'] in ('register', 'create', 'mount'):
            # compile pwd entry name
            args['pwd_entry'] = 'efst-entry-{}'.format(args['entry_name'])

            if args['sub_cmd'] in ('register', 'create'):
                if not args['mountpoint_path']:
                    # compile mount volume path
                    unique_names_checker = UniqueDirNamesChecker(OSConfig.MOUNTPOINT_FOLDER)
                    mountpoint = unique_names_checker.unique_name(format(args['entry_name']))
                    args['mountpoint_path'] = os.path.join(OSConfig.MOUNTPOINT_FOLDER, mountpoint)

                # if not specified, compile mount name as well
                if not args['mount_name']:
                    args['mount_name'] = args['entry_name']

                # conf/key path
                default_cfg_path = os.path.join(args['backend_path'], EncFSHandler.DEFAULT_CFG_FNAME)
                if not args['conf_path']:
                    # if no conf path specified, try out the default
                    args['conf_path'] = default_cfg_path

                if args['sub_cmd'] == 'register':
                    if not os.path.exists(args['conf_path']):
                        print('The config file was not found at location: \n\t"{}"'.format(args['conf_path']))
                        print('Please specify the correct config file using the "--conf-path" option')
                        parser.exit()

                if args['sub_cmd'] == 'create':
                    if os.path.exists(args['conf_path']):
                        # using default path
                        if args['conf_path'] == default_cfg_path:
                            print('The directory already seems to be an EncFS backend store with existing conf. file: \n\t"{0}"' \
                                  '\n\t"{1}"'.format(args['backend_path'], default_cfg_path))
                            print('To setup a directory as multiple interleaved EncFS Backends, use the "--conf-path" option'
                                  'to explicitly specify the new conf/key file')
                            parser.exit()
                        else:
                            print('EncFS conf/key file already exists: \n\t"{}"'.format(args['conf_path']))
                            print('To register an existing backend store, run "efst register -h"')
                            parser.exit()

    # Options parsing
    @classmethod
    def parse_commands(cls, parser):
        ''' Commands parsing
        '''
        subparsers = parser.add_subparsers(dest = 'sub_cmd', title = 'EFSM commands',
                                        metavar = '{create, register, unregister, mount, umount, version}')
        cls._add_version(subparsers)

        # Create
        create_parser = subparsers.add_parser('create',
                                   description = 'Sets up and register EncFS backend folder and its corresponding view',
                                   formatter_class=EFSTHelpFormatter)
        cls._add_entry_groups(create_parser, action_type = ConfKeyActionType.Create)
        cls._add_config_entry(create_parser)

        # Register
        register_parser = subparsers.add_parser('register',
                                   description = 'Register EncFS backend folder and sets up its corresponding view',
                                   formatter_class=EFSTHelpFormatter)
        cls._add_entry_groups(register_parser, action_type = ConfKeyActionType.Register)

        # Unregister
        unregister_parser = subparsers.add_parser('unregister',
                                   description = 'Removes a registered EncFS entry',
                                             formatter_class=EFSTHelpFormatter)
        cls._add_entry_name(unregister_parser, registered_only = True, help = "Name of entry to unregister")

        # Mount
        mount_parser = subparsers.add_parser('mount',
                                             description = 'Mounts a registered EncFS entry',
                                             formatter_class=EFSTHelpFormatter)
        cls._add_entry_name(mount_parser, registered_only = True, help = "Name of registered entry to mount")

        # Umount
        umount_parser = subparsers.add_parser('umount',
                                             description = 'Un-mounts a registered EncFS entry',
                                             formatter_class=EFSTHelpFormatter)
        cls._add_entry_name(umount_parser, registered_only = True, help = "Name of registered entry to un-mount")


    @classmethod
    def parse_options(cls, script_name = None, description = None):
        ''' EFSM Options parsing workflow
        '''
        return super().parse_options(script_name = 'efsm',
                                            description = '''
                                                EFSM is a part of EFST tools. It enables create and register EncFS backend stores, and
                                                then easily manipulate corresponding ciphered / plaintext views.
                                              ''')

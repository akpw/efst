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
from efst.encfs.encfs_cfg import EncFSCFG
from efst.config.efst_config import config_handler, EFSTConfigKeys, EntryTypes
from efst.utils.efst_utils import FSHelper, UniqueDirNamesChecker, UniquePartialMatchList


class EFSMCommands(EFSTCommands):
    CREATE = 'create'
    MOUNT = 'mount'
    UMOUNT = 'umount'

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        '{}, '.format(cls.CREATE),
                        '{}, '.format(cls.REGISTER),
                        '{}, '.format(cls.UNREGISTER),
                        '{}, '.format(cls.SHOW),
                        '{}, '.format(cls.MOUNT),
                        '{}, '.format(cls.UMOUNT),
                        '{}, '.format(cls.INFO),
                        '{}'.format(cls.VERSION),
                        '}'))


class ConfKeyActionType(IntEnum):
    ''' Defines EFS entries types
    '''
    Create = 0
    Register = 1


class EFSMOptionsParser(EFSTOptionsParser):
    ''' EFSM Options Parser
    '''
    def __init__(self):
        self._script_name = 'EFSM'
        self._description = \
    '''
    EFSM is a part of EFST tools.
    It enables creating new and registering
    existing EncFS backend store directories as well as
    related assets such as target mountpoint folder,
    mount volume name, path to EncFS config/key file,
    safely-stored passwords, etc.
    Once registered, these EFST entries can be easily
    manipulated in a single simple command.
    '''

    # Options parsing
    def parse_commands(self, parser):
        ''' Commands parsing
        '''
        subparsers = parser.add_subparsers(dest = 'sub_cmd',
                                                title = 'EFSM commands',
                                                        metavar = EFSMCommands.commands_meta())
        self._add_version(subparsers)
        self._add_info(subparsers)

        # Create
        create_parser = subparsers.add_parser(EFSMCommands.CREATE,
                                   description = 'Sets up and register EncFS backend folder and its corresponding view',
                                   formatter_class=EFSTHelpFormatter)
        self._add_entry_groups(create_parser, action_type = ConfKeyActionType.Create)
        self._add_config_entry(create_parser)

        # Register
        register_parser = subparsers.add_parser(EFSMCommands.REGISTER,
                                   description = 'Register EncFS backend folder and sets up its corresponding view',
                                   formatter_class=EFSTHelpFormatter)
        self._add_entry_groups(register_parser, action_type = ConfKeyActionType.Register)

        # Show
        show_parser = subparsers.add_parser(EFSMCommands.SHOW,
                                   description = 'Shows a registered EncFS entry',
                                             formatter_class=EFSTHelpFormatter)
        required_args_group = show_parser.add_argument_group('Required Arguments')
        self._add_entry_name(required_args_group, registered_only = True, help = "Name of entry to show")


        # Unregister
        unregister_parser = subparsers.add_parser(EFSMCommands.UNREGISTER,
                                   description = 'Removes a registered EncFS entry',
                                             formatter_class=EFSTHelpFormatter)
        required_args_group = unregister_parser.add_argument_group('Required Arguments')
        self._add_entry_name(required_args_group, registered_only = True, help = "Name of entry to unregister")

        # Mount
        mount_parser = subparsers.add_parser(EFSMCommands.MOUNT,
                                             description = 'Mounts a registered EncFS entry',
                                             formatter_class=EFSTHelpFormatter)
        required_args_group = mount_parser.add_argument_group('Required Arguments')
        self._add_entry_name(required_args_group, registered_only = True, help = "Name of registered entry to mount")

        # Umount
        umount_parser = subparsers.add_parser(EFSMCommands.UMOUNT,
                                             description = 'Un-mounts a registered EncFS entry',
                                             formatter_class=EFSTHelpFormatter)
        required_args_group = umount_parser.add_argument_group('Required Arguments')
        self._add_entry_name(required_args_group, registered_only = True, help = "Name of registered entry to un-mount")


    # Options checking
    def _check_cmd_args(self, args, parser):
        ''' Validation of supplied CLI commands
        '''
        super()._check_cmd_args(args, parser)
        if args['sub_cmd'] in (EFSMCommands.VERSION, EFSMCommands.INFO):
            # not much to check there
           pass

        elif args['sub_cmd'] not in (EFSMCommands.REGISTER, EFSMCommands.CREATE):
            # Registered Entry name could be a partial match, need to expand
            args['entry_name'] = UniquePartialMatchList(
                                        config_handler.registered_entries()).find(args['entry_name'])

            if args['entry_name'] == EFSTConfigKeys.NO_ENTRIES_REGISTERED:
                print('No suitable config entry to {}'.format(args['sub_cmd']))
                print('To set up and register a new EncFS backend entry: \n\t $ efsm create -h')
                print('To register an existing EncFS backend entry: \n\t $ efsm register -h')
                parser.exit()

        elif args['sub_cmd'] in (EFSMCommands.REGISTER, EFSMCommands.CREATE, EFSMCommands.MOUNT):
            # compile pwd entry name
            args['pwd_entry'] = 'efst-entry-{}'.format(args['entry_name'])

            if args['sub_cmd'] in (EFSMCommands.REGISTER, EFSMCommands.CREATE):
                if args['entry_name'] in (config_handler.registered_entries()):
                    entry = config_handler.entry(args['entry_name'])
                    print('"{0}": entry name already registered as a {1} Entry'.format(args['entry_name'],
                        'Reversed CipherText' if entry.entry_type == EntryTypes.ReversedCipherText else 'CipherText'))
                    parser.exit()

                if not args['mountpoint_path']:
                    # compile mount volume path
                    unique_names_checker = UniqueDirNamesChecker(config_handler.os_config.mountpoint_folder)
                    mountpoint = unique_names_checker.unique_name(format(args['entry_name']))
                    args['mountpoint_path'] = os.path.join(config_handler.os_config.mountpoint_folder, mountpoint)

                # if not specified, compile mount name as well
                if not args['mount_name']:
                    args['mount_name'] = args['entry_name']

                # conf/key path
                default_cfg_path = os.path.join(args['backend_path'], EncFSCFG.DEFAULT_CFG_FNAME)
                if not args['conf_path']:
                    # if no conf path specified, try out the default
                    args['conf_path'] = default_cfg_path

                if args['sub_cmd'] == EFSMCommands.REGISTER:
                    if not os.path.exists(args['conf_path']):
                        print('The config file was not found at location: \n\t"{}"'.format(args['conf_path']))
                        print('Please specify the correct config file using the "--conf-path" option')
                        parser.exit()

                elif args['sub_cmd'] == EFSMCommands.CREATE:
                    # Configuration Entry name could be a partial match, need to expand
                    args['config_entry'] = UniquePartialMatchList(
                                        config_handler.registered_encfs_cfg_entries()).find(args['entry_name'])

                    if os.path.exists(args['conf_path']):
                        # using default path
                        if args['conf_path'] == default_cfg_path:
                            print('The directory already seems to be an EncFS backend store with existing conf. file: \n\t"{0}"' \
                                  '\n\t"{1}"'.format(args['backend_path'], default_cfg_path))
                            print('To setup a directory as multiple interleaved EncFS Backends, use the "--conf-path" option'
                                  'to explicitly specify the new conf/key file')
                            parser.exit()
                        else:
                            if os.path.isdir(args['conf_path']):
                                args['conf_path'] = os.path.join(args['conf_path'], EncFSCFG.DEFAULT_CFG_FNAME)

                            # still exists...
                            if os.path.exists(args['conf_path']):
                                print('EncFS conf/key file already exists: \n\t"{}"'.format(args['conf_path']))
                                print('To register an existing backend store, run "efst register -h"')
                                parser.exit()

    @property
    def _default_command(self):
        ''' Default to showing help
        '''
        return None

    # Helpers
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
            type = (lambda bpath:FSHelper.full_path(bpath)) \
                    if action_type == ConfKeyActionType.Create \
                        else (lambda bpath: cls._is_valid_dir_path(parser, bpath)),
            required = True,
            help = 'Path to the back-end store folder. ' \
                'The backend folder typically contains your ciphered data, for which a plaintext view folder is set up and registered. ' \
                'That can reversed via the "--reverse" switch, which results in an on-demand ciphered view for your plaintext back-end data')

        optional_args_group = parser.add_argument_group('Additional Arguments')
        # Conf path
        def _conf_path_checker(cpath):
            if action_type == ConfKeyActionType.Create:
                return FSHelper.full_path(cpath, check_parent_path = True)
            else:
                return cls._is_valid_file_path(parser, cpath)

        optional_args_group.add_argument('-cp', '--conf-path', dest = 'conf_path',
                        type = lambda cpath:_conf_path_checker(cpath),
                        help = '{0}ath to the EncFS conf/key file. ' \
                            'If ommitted, a default one will be {1} in the back-end folder'.format(
                                   'P' if action_type == ConfKeyActionType.Register else 'Target p',
                                   'looked up for' if action_type == ConfKeyActionType.Register else 'created'))
        optional_args_group.add_argument("-r", "--reverse", dest='reverse',
                    help = "Enables reverse mode, i.e. a ciphered view for a plaintext back-end data",
                    action='store_true')
        optional_args_group.add_argument("-i", "--idle", dest='idle_minutes',
                    help = "Auto unmount after a period of inactivity (in minutes)",
                    default = 0)
        optional_args_group.add_argument('-mp', '--mountpoint-path', dest = 'mountpoint_path',
            type = lambda mpath: cls._is_valid_dir_path(parser, mpath),
            help = 'Path to the mountpoint folder. If omitted, will be auto-generated from ' \
                                        'entry name and put in the "{}" folder'.format(config_handler.os_config.mountpoint_folder))
        optional_args_group.add_argument('-mn', '--mount-name', dest = 'mount_name',
                        type = str,
                        help = 'Mounted volume name. If ommitted, the entry name will be used')



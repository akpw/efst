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

class EFSCCommands(EFSTCommands):
    CREATE_KEY = 'create-key'

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        '{}, '.format(cls.CREATE_KEY),
                        '{}, '.format(cls.REGISTER),
                        '{}, '.format(cls.UNREGISTER),
                        '{}, '.format(cls.SHOW),
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
        A part of EFST tools, EFSC is a
        configuration utility for managing EncFS
        presets used for creating EncFS config files.
        Out of the box, EFST come with a default built-in
        configuration that can be viewed via:

            $ efsc show -ce EFST
    '''

    # Options parsing
    def parse_commands(self, parser):
        ''' Commands parsing
        '''
        subparsers = parser.add_subparsers(dest = 'sub_cmd', title = 'EFSC commands',
                                                                            metavar = EFSCCommands.commands_meta())
        self._add_version(subparsers)
        self._add_info(subparsers)

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


        # Show EFST Config Entry
        show_parser = subparsers.add_parser(EFSCCommands.SHOW,
                                   description = 'Shows a registered EFST Config entry',
                                             formatter_class=EFSTHelpFormatter)
        required_args_group = show_parser.add_argument_group('Required Arguments')
        self._add_cfg_entry_name(required_args_group, registered_only = True, help = "Name of EFST Config entry to show")

        # Register EFST Config
        register_parser = subparsers.add_parser(EFSCCommands.REGISTER,
                                   description = 'Registers an EFST config entry',
                                             formatter_class=EFSTHelpFormatter)
        required_args_group = register_parser.add_argument_group('Required Arguments')
        self._add_cfg_entry_name(required_args_group, registered_only = False, help = "Name of EFST Config Entry to register")

        optional_args_group = register_parser.add_argument_group('Additional Arguments')
        optional_args_group.add_argument('-ca', '--cipher-algorithm', dest = 'cipher_algorithm',
                        type = str,
                        choices = EncFSCipherAlg.alg_names(),
                        default = EncFSCipherAlg.AES.name,
                        help = 'EncFS Cipher Algorithm, "{}" by default'.format(EncFSCipherAlg.AES.name))
        optional_args_group.add_argument('-ks', '--key-size', dest = 'key_size',
                        type = int,
                        metavar = EncFSCipherAlg.key_size_msg(),
                        default = EncFSCipherAlg.default_key_size(),
                        help = 'EncFS Cipher Algorithm  Key Size in bits, {} by default'.format(EncFSCipherAlg.default_key_size()))
        optional_args_group.add_argument('-bs', '--block-size', dest = 'block_size',
                        type = int,
                        metavar = EncFSCipherAlg.block_size_msg(),
                        default = config_handler.os_config.os_block_size,
                        help = 'EncFS Cipher Algorithm  Block Size in bytes. If omitted, system default ({}) will be used'.format(config_handler.os_config.os_block_size))
        optional_args_group.add_argument('-na', '--filename-algorithm', dest = 'filename_algorithm',
                        type = str,
                        choices = EncFSNameAlg.alg_names(),
                        default = EncFSNameAlg.Stream.name,
                        help = 'EncFS Filename Encoding Algorithm, "{}" by default'.format(EncFSNameAlg.Stream.name))

        advanced_args_group = register_parser.add_argument_group('Advanced Arguments')
        advanced_args_group.add_argument("-cn", "--chained-name", dest='chainedNameIV',
                    help = 'Enables filename IV chaining, ' \
                            'making filename encoding dependent on the complete path ' \
                            'rather then encoding each path element individually',
                    action='store_true')
        advanced_args_group.add_argument("-uv", "--unique-iv", dest='uniqueIV',
                    help = 'Enables per-file initialization vectors, ' \
                            'adding 8 bytes per file to the storage requirements ',
                    action='store_true')
        advanced_args_group.add_argument("-bh", "--block-headers", dest='blockMACBytes',
                    help = 'Enables per-block authentication code header on every block in a file, ' \
                            'adding 12 bytes per each block',
                    action='store_true')
        advanced_args_group.add_argument("-rb", "--block-random-bytes", dest='blockMACRandBytes',
                    type = int,
                    choices = [rb for rb in range(0,9)],
                    metavar = '{A number of bytes, from 0 (no random bytes) to 8}',
                    default = 0,
                    help = 'Adds random bytes to each block header, ' \
                            'ensuring different block authentication codes')
        advanced_args_group.add_argument("-dh", "--disable-holes", dest='disable_holes',
                    help = 'Disables file-hole pass-through, writing encrypted blocks when file holes are created',
                    action='store_true')


        # Un-Register EFST Config
        unregister_parser = subparsers.add_parser(EFSCCommands.UNREGISTER,
                                   description = 'Un-registers an EFST config entry',
                                             formatter_class=EFSTHelpFormatter)
        required_args_group = unregister_parser.add_argument_group('Required Arguments')
        self._add_cfg_entry_name(required_args_group, registered_only = True, help = "Name of EFST Config entry to unregister")


    # Options checking
    def _check_cmd_args(self, args, parser):
        ''' Validation of supplied CLI commands
        '''
        super()._check_cmd_args(args, parser)
        if args['sub_cmd'] in (EFSCCommands.SHOW, EFSCCommands.UNREGISTER, EFSCCommands.CREATE_KEY):
            # Registered Entry name could be a partial match, need to expand
            args['config_entry'] = UniquePartialMatchList(
                                        config_handler.registered_encfs_cfg_entries()).find(args['config_entry'])

            # Create Key
            if args['sub_cmd'] == EFSCCommands.CREATE_KEY:
                if os.path.exists(args['conf_path']):
                    # if target path is directory, compile default file name
                    if os.path.isdir(args['conf_path']):
                        args['conf_path'] = os.path.join(args['conf_path'], EncFSCFG.DEFAULT_CFG_FNAME)
                    else:
                        print('EncFS conf/key file already exists: \n\t"{}"'.format(args['conf_path']))
                        parser.exit()

        # Register an EncFS Config
        elif args['sub_cmd'] in EFSCCommands.REGISTER:
            if args['config_entry'] in (config_handler.registered_encfs_cfg_entries()):
                print('"{0}": entry name already registered'.format(args['config_entry']))
                parser.exit()

            # algorithms
            args['cipher_algorithm'] = EncFSCipherAlg.alg_type_by_name(args['cipher_algorithm'])
            args['filename_algorithm'] = EncFSNameAlg.alg_type_by_name(args['filename_algorithm'])

            # key size
            if args['key_size'] not in EncFSCipherAlg.key_sizes(alg_type = args['cipher_algorithm']):
                print('"{}": Wrong Key Size value'.format(args['key_size']))
                print(EncFSCipherAlg.key_size_msg(alg_type = args['cipher_algorithm']))
                parser.exit()

            # block size
            if args['block_size'] not in EncFSCipherAlg.block_sizes(alg_type = args['cipher_algorithm']):
                print('"{}": Wrong Block Size value'.format(args['block_size']))
                print(EncFSCipherAlg.block_size_msg(alg_type = args['cipher_algorithm']))
                parser.exit()

    @property
    def _default_command(self):
        ''' Default to showing help
        '''
        return None

    # Helpers
    @staticmethod
    def _add_cfg_entry_name(parser, registered_only = False, help = 'EncFS Config Entry name'):
        parser.add_argument('-ce', '--config-entry', dest = 'config_entry',
                        type = str,
                        metavar = config_handler.registered_encfs_cfg_entries() if registered_only else None,
                        required = True,
                        choices = UniquePartialMatchList(
                                        config_handler.registered_encfs_cfg_entries()) if registered_only else None,
                        help = help)



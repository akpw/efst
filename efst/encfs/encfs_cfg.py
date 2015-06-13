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
from enum import Enum, unique
from collections import namedtuple


''' EncFS Config Options Helpers
'''

class EncFSCFG:
    ''' EncFS Configuration Entry
    '''

    # EncFS Cfg Key Entry
    EncFSCfgEntry = namedtuple('EncFSCfgEntry',['cipherAlg', 'keySize', 'blockSize',
                                                'nameAlg', 'chainedNameIV', 'uniqueIV',
                                                'blockMACBytes', 'blockMACRandBytes', 'allowHoles'])
    DEFAULT_CFG_FNAME = '.encfs6.xml'


@unique
class EncFSAlgorithms(Enum):
    ''' EncFS Cipher / Filname Algorithms Options Helpers
    '''
    @classmethod
    def alg_names(cls):
        ''' Supported algorithms names
        '''
        return [alg_name.name for alg_name in cls]

    @classmethod
    def alg_type_by_name(cls, alg_name):
        ''' Algorithms type by name
        '''
        for alg in cls:
            if alg.name == alg_name:
                return alg
        return None

    @classmethod
    def alg_name_by_type(cls, alg_type):
        ''' Algorithms name by type
        '''
        if alg_type in cls:
            # if alg_type is a clean enum type, just return the associated name
            return cls(alg_type).name
        else:
            # try to look by int value
            try:
                alg_type = int(alg_type)
            except ValueError:
                pass
            else:
                for en in cls:
                    if en.value == alg_type:
                        return en.name
            return 'Algorithm type not supported'


class EncFSCipherAlg(EncFSAlgorithms):
    ''' EncFS Cipher Algorithm Options Helper
    '''
    AES = 1
    Blowfish = 2

    @staticmethod
    def default_key_size():
        return 256

    @staticmethod
    def default_block_size():
        return 1024

    @classmethod
    def key_sizes(cls, alg_type = None):
        if not alg_type:
            alg_type = cls.AES

        if alg_type == cls.AES:
            return [128, 192, 256]
        else:
            return [128, 160, 192, 224, 256]

    @classmethod
    def block_sizes(cls, alg_type = None):
        if not alg_type:
            alg_type = cls.AES

        if alg_type == cls.AES:
            return [block_size for block_size in range(64, 4097, 16)]
        else:
            return [block_size for block_size in range(64, 4097, 8)]

    @classmethod
    def key_size_msg(cls, alg_type = None):
        if not alg_type:
            return '{from 128 to 256 bits in increments of 64 (AES) or 32 (Blowfish)}'

        if alg_type == cls.AES:
            return 'AES supports key sizes from 128 to 256 bits in increments of 64 bits, i.e. {128, 192, 256}'
        else:
            return 'Blowfish supports key sizes from 128 to 256 bits in increments of 32 bits, i.e. {128, 160, 192, 224, 256}'

    @classmethod
    def block_size_msg(cls, alg_type = None):
        if not alg_type:
            return '{from 64 to 4096 bytes in increments of 16 (AES) or 8 (Blowfish)}'

        if alg_type == cls.AES:
            return 'AES supports block sizes from 64 to 4096 bytes in increments of 16'
        else:
            return 'Blowfish supports block sizes from 64 to 4096 bytes in increments of 8'


class EncFSNameAlg(EncFSAlgorithms):
    ''' EncFS Filename Algorithm Options Helper
    '''
    Block = 1
    Block32 = 2
    Plain  = 3
    Stream  = 4


class EncFSUtils:
    ''' EncFS Utils
    '''
    @staticmethod
    def encfs_installed():
        """ Checks if encfs is installed and in system PATH
        """
        if os.name == 'nt':
            print('Windows OS is not supported')
        else:
            encfs_app_name = 'encfs'
            for path in os.environ['PATH'].split(os.pathsep):
                app_path = os.path.join(path, encfs_app_name)
                if os.path.isfile(app_path) and os.access(app_path, os.X_OK):
                    return True
        return False


class EncFSNotInstalled(Exception):
    def __init__(self, message = None):
        super().__init__(message if message is not None else self.default_message)

    @property
    def default_message(self):
        if os.name == 'nt':
            msg = \
        '''
        Windows OS is not currently supported.

        To work with files encrypted with EFST on

        supported platforms, use Windows EncFS-compatible

        software like Boxcryptor or encfs4win.

        '''
        else:
            msg = \
        '''

        Looks like EncFS is not installed.

        Please install EncFS and make it

        available in the command line.

        '''

        return msg

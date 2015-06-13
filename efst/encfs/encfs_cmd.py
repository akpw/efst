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

import sys, shlex, pexpect, io
from efst.encfs.encfs_cfg import EncFSNameAlg
from efst.config.efst_config import config_handler

''' EncFS Commands Helpers
'''

class EncFSCommands:
    @staticmethod
    def build_cmd(encfs_dir_path, mount_dir_path, unmount_on_idle = None,
                            reverse = False, enc_cfg_path = None, mount_name = None, pwd = None):
        ''' Builds appropriate EnFS command
        '''
        cmd = ''.join((
                        'echo {} | '.format(pwd) if pwd else '',
                        ' ENCFS6_CONFIG={}'.format(shlex.quote(enc_cfg_path)) if enc_cfg_path else '',
                        ' encfs',
                        ' -S' if pwd else '',
                        ' --reverse' if reverse else '',
                        ' --idle {}'.format(unmount_on_idle) if unmount_on_idle else '',
                        ' {}'.format(shlex.quote(encfs_dir_path)),
                        ' {}'.format(shlex.quote(mount_dir_path)),
                        ' {0}{1}'.format(config_handler.os_config.volname_cmd, shlex.quote(mount_name)) \
                                                if (config_handler.os_config.volname_cmd and mount_name) else ''
                        ))
        return cmd.strip()

    @staticmethod
    def run_expectant_cmd(cmd, cfg_entry, pwd):
        ''' Creates new EncFS conf/key file
        '''
        print('Creating EncFS backend store...')

        child = pexpect.spawnu(cmd)

        child.expect('>')
        child.sendline('x')

        child.expect('The following cipher algorithms are available')
        child.sendline(cfg_entry.cipherAlg)

        child.expect('Selected key size')
        child.sendline(cfg_entry.keySize)

        child.expect('filesystem block size')
        child.sendline(cfg_entry.blockSize)

        output = io.StringIO()
        child.logfile_read = output
        child.expect('The following filename encoding algorithms are available')
        child.logfile_read = None

        # filename encoding
        name_alg = cfg_entry.nameAlg
        lines = output.getvalue().split('\n')
        for line in lines:
            if line.startswith('3. Stream'):
                # Block32 not supported, need to adjust the numbering
                if name_alg != EncFSNameAlg.Block.value:
                    name_alg = int(name_alg)
                    if name_alg == EncFSNameAlg.Block32.value:
                        # if Block32 was explicitly attempted, notify
                        print('Block32 file name encoding not supported')
                        print('Using Block file name encoding instead')
                    name_alg -= 1
                    name_alg = str(name_alg)
        child.sendline(name_alg)

        child.expect('Enable filename initialization vector chaining')
        child.sendline(cfg_entry.chainedNameIV)

        child.expect('Enable per-file initialization vectors')
        child.sendline(cfg_entry.uniqueIV)

        child.expect('Enable block authentication code headers')
        child.sendline(cfg_entry.blockMACBytes)

        child.expect('Add random bytes to each block header')
        child.sendline(cfg_entry.blockMACRandBytes)

        child.expect('Enable file-hole pass-through')
        child.sendline(cfg_entry.allowHoles)

        child.expect('New Encfs Password')
        child.sendline(pwd)

        child.expect('Verify Encfs Password')
        child.sendline(pwd)

        child.expect(pexpect.EOF, timeout=None)
        child.close()

        if child.exitstatus == 0:
            return True

        return False



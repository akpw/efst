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

import os, sys, shlex, pexpect
from collections import namedtuple
from efst.utils.efst_utils import run_cmd, CmdProcessingError, temp_dir, FSHelper


class EncFSHandler:
    ''' EncFS operations handler
    '''

    # EncFS Cfg Key Entry
    EncFSCfgEntry = namedtuple('EncFSCfgEntry',
                                        ['cipherAlg', 'keySize', 'blockSize',
                                         'nameAlg', 'chainedNameIV', 'uniqueIV',
                                         'blockMACBytes', 'blockMACRandBytes', 'allowHoles'])
    DEFAULT_CFG_FNAME = '.encfs6.xml'

    @staticmethod
    def create_cfg_file(pwd, cfg_entry, cfg_target_path):
        with temp_dir() as tmp_encfs:
            with temp_dir() as tmp_mount:
                cmd = EncFSHandler._build_cmd(encfs_dir_path = tmp_encfs, mount_dir_path = tmp_mount)

                EncFSHandler._run_expectant_cmd(cmd, cfg_entry, pwd)
                EncFSHandler.umount(tmp_mount, quiet = True)

                cfg_name = os.path.join(tmp_encfs, EncFSHandler.DEFAULT_CFG_FNAME)
                if os.path.exists(cfg_name):
                    if os.path.isdir(cfg_target_path):
                        # if target path is directory,
                        # compile default file name
                        cfg_target_path = os.path.join(cfg_target_path, EncFSHandler.DEFAULT_CFG_FNAME)

                    if FSHelper.move_FS_entry(cfg_name, cfg_target_path, quiet = True):
                        return True
                    else:
                        print('Error creating conf/key file at requested location:\n\t"{}"'.format(cfg_target_path))
        return False

    @staticmethod
    def mount(pwd, enc_cfg_path, encfs_dir_path,
                    mount_dir_path, mount_name, reverse = False):
        # validate inputs
        if enc_cfg_path and not os.path.exists(enc_cfg_path):
            print('Wrong conf/key path: {}'.format(enc_cfg_path))
            return False

        if not os.path.exists(encfs_dir_path):
            print('Wrong backend folder path: {}'.format(encfs_dir_path))
            return False

        if not os.path.exists(mount_dir_path):
            os.mkdir(mount_dir_path)
        elif os.path.ismount(mount_dir_path):
            print('Already Mounted: {}'.format(mount_dir_path))
            return False

        cmd = EncFSHandler._build_cmd(encfs_dir_path = encfs_dir_path,
                              mount_dir_path = mount_dir_path,
                              reverse = reverse, enc_cfg_path = enc_cfg_path,
                              mount_name = mount_name, pwd = pwd)
        try:
            run_cmd(cmd, shell = True)
        except CmdProcessingError as e:
            print ('Error while mounting: {}'.format(e.args[0]))
            return False
        else:
            print('Mounted: {}'.format(mount_dir_path))
            return True

    @staticmethod
    def umount(mount_dir_path, quiet = False):
        if not (os.path.exists(mount_dir_path) and os.path.ismount(mount_dir_path)):
            if not quiet:
                print('Not Mounted: {}'.format(mount_dir_path))
            return False

        cmd = 'umount {}'.format(shlex.quote(mount_dir_path))
        try:
            run_cmd(cmd, shell = True)
        except CmdProcessingError as e:
            if not quiet:
                print ('Error while unmounting: {}'.format(e.msg))
            return False
        else:
            if not quiet:
                print('Unmounted: {}'.format(mount_dir_path))
            return True

    # Internal Helpers
    @staticmethod
    def _build_cmd(encfs_dir_path, mount_dir_path,
                            reverse = False, enc_cfg_path = None, mount_name = None, pwd = None):
        ''' Builds appropriate EnFS command
        '''
        cmd = ''.join((
                        'echo {} | '.format(pwd) if pwd else '',
                        ' ENCFS6_CONFIG={}'.format(shlex.quote(enc_cfg_path)) if enc_cfg_path else '',
                        ' encfs',
                        ' -S' if pwd else '',
                        ' --reverse' if reverse else '',
                        ' {}'.format(shlex.quote(encfs_dir_path)),
                        ' {}'.format(shlex.quote(mount_dir_path)),
                        ' -o volname={}'.format(shlex.quote(mount_name)) if mount_name else ''
                        ))
        return cmd.strip()

    @staticmethod
    def _run_expectant_cmd(cmd, cfg_entry, pwd):
        ''' Creates new EncFS conf/key file
        '''

        print('Creating EncFS backend store...')

        child = pexpect.spawnu(cmd)
        #child.logfile = sys.stdout

        child.expect('>')
        child.sendline('x')

        child.expect('The following cipher algorithms are available')
        child.sendline(cfg_entry.cipherAlg)

        child.expect('Selected key size')
        child.sendline(cfg_entry.keySize)

        child.expect('filesystem block size')
        child.sendline(cfg_entry.blockSize)

        child.expect('The following filename encoding algorithms are available')
        child.sendline(cfg_entry.nameAlg)

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



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

import os, shlex
from efst.encfs.encfs_cfg import EncFSCFG
from efst.encfs.encfs_cmd import EncFSCommands
from efst.utils.efst_utils import run_cmd, CmdProcessingError, temp_dir, FSHelper
from efst.config.efst_config import config_handler


class EncFSHandler:
    ''' EncFS operations handler
    '''
    @staticmethod
    def create_cfg_file(pwd, cfg_entry, cfg_target_path):
        ''' Creates EncFS Conf/Key file at a given target path
        '''
        with temp_dir() as tmp_encfs:
            with temp_dir() as tmp_mount:
                cmd = EncFSCommands.build_cmd(encfs_dir_path = tmp_encfs, mount_dir_path = tmp_mount)

                EncFSCommands.run_expectant_cmd(cmd, cfg_entry, pwd)
                EncFSHandler.umount(tmp_mount, quiet = True)

                cfg_name = os.path.join(tmp_encfs, EncFSCFG.DEFAULT_CFG_FNAME)
                if os.path.exists(cfg_name):
                    if os.path.isdir(cfg_target_path):
                        # if target path is directory,
                        # compile default file name
                        cfg_target_path = os.path.join(cfg_target_path, EncFSCFG.DEFAULT_CFG_FNAME)

                    if FSHelper.move_FS_entry(cfg_name, cfg_target_path, quiet = True):
                        return True
                    else:
                        print('Error creating conf/key file at requested location:\n\t"{}"'.format(cfg_target_path))
        return False

    @staticmethod
    def mount(pwd, enc_cfg_path, encfs_dir_path, mount_dir_path,
                                    mount_name, reverse = False, unmount_on_idle = None, quiet = False):
        ''' Mounts exisiting EncFS backened
        '''
        # validate inputs
        if enc_cfg_path and not os.path.exists(enc_cfg_path):
            if not quiet:
                print('Wrong conf/key path: {}'.format(enc_cfg_path))
            return False

        if not os.path.exists(encfs_dir_path):
            if not quiet:
                print('Wrong backend folder path: {}'.format(encfs_dir_path))
            return False

        if not os.path.exists(mount_dir_path):
            os.mkdir(mount_dir_path)
        elif os.path.ismount(mount_dir_path):
            if not quiet:
                print('Already Mounted: {}'.format(mount_dir_path))
            return False

        cmd = EncFSCommands.build_cmd(encfs_dir_path = encfs_dir_path,
                              mount_dir_path = mount_dir_path,
                              reverse = reverse, unmount_on_idle = unmount_on_idle,
                              enc_cfg_path = enc_cfg_path,
                              mount_name = mount_name, pwd = pwd)
        try:
            run_cmd(cmd, shell = True)
        except CmdProcessingError as e:
            if not quiet:
                print ('Error while mounting: {}'.format(e.args[0]))
            return False
        else:
            if not quiet:
                print('Mounted: {}'.format(mount_dir_path))
            return True

    @staticmethod
    def umount(mount_dir_path, quiet = False):
        ''' Un-mounts an mounted EncFS backened
        '''
        if not (os.path.exists(mount_dir_path) and os.path.ismount(mount_dir_path)):
            if not quiet:
                print('Not Mounted: {}'.format(mount_dir_path))
            return False

        cmd = '{0} {1}'.format(config_handler.os_config.umount_cmd, shlex.quote(mount_dir_path))
        try:
            run_cmd(cmd, shell = True)
        except CmdProcessingError as e:
            if not quiet:
                print ('Error while unmounting: {}'.format(e.args[0]))
            return False
        else:
            if not quiet:
                print('Unmounted: {}'.format(mount_dir_path))
            return True






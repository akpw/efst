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

import os, shlex, shutil, copy
from efst.encfs.encfs_cfg import EncFSCFG
from efst.encfs.encfs_cmd import EncFSCommands
from efst.utils.efst_utils import run_cmd, CmdProcessingError, temp_dir, FSHelper
from efst.config.efst_config import config_handler


class EncFSHandler:
    ''' EncFS operations handler
    '''
    @classmethod
    def create_cfg_file(cls, pwd, cfg_entry, cfg_target_path):
        ''' Creates EncFS Conf/Key file at a given target path
        '''
        with temp_dir() as tmp_encfs:
            with temp_dir() as tmp_mount:
                cmd = EncFSCommands.build_cmd(encfs_dir_path = tmp_encfs, mount_dir_path = tmp_mount)

                # if needed, temporarily reset the ENCFS6_CONFIG env variable
                encfs6_config_backup = cls._encfs6_config_backup_and_reset()

                EncFSCommands.run_expectant_cmd(cmd, cfg_entry, pwd)
                cls.umount(tmp_mount, quiet = True)

                # if needed, restore the ENCFS6_CONFIG env variable
                cls._encfs6_config_restore(encfs6_config_backup)

                cfg_name = os.path.join(tmp_encfs, EncFSCFG.DEFAULT_CFG_FNAME)
                if os.path.exists(cfg_name):
                    if os.path.isdir(cfg_target_path):
                        # if target path is directory,
                        # compile default file name
                        cfg_target_path = os.path.join(cfg_target_path, EncFSCFG.DEFAULT_CFG_FNAME)

                    if FSHelper.move_FS_entry(cfg_name, cfg_target_path, quiet = True):
                        return True
        return False

    @classmethod
    def mount(cls, pwd, enc_cfg_path, encfs_dir_path, mount_dir_path,
                                    mount_name, reverse = False, unmount_on_idle = None, quiet = False):
        ''' Mounts an exisiting EncFS backened
        '''
        # validate inputs
        result = False
        if not cls._check_args(encfs_dir_path = encfs_dir_path,
                                                enc_cfg_path = enc_cfg_path, quiet = quiet):
            return result

        if not os.path.exists(mount_dir_path):
            os.mkdir(mount_dir_path)
        elif os.path.ismount(mount_dir_path):
            if not quiet:
                print('Already Mounted: {}'.format(mount_dir_path))
            return result

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
        else:
            if not quiet:
                print('Mounted: {}'.format(mount_dir_path))
            result = True

        return result

    @staticmethod
    def umount(mount_dir_path, quiet = False):
        ''' Un-mounts a mounted EncFS backened
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

    @classmethod
    def backend_info(cls, encfs_dir_path, enc_cfg_path, quiet = False):
        ''' EncFS backened general info
        '''
        # validate inputs
        if not cls._check_args(encfs_dir_path = encfs_dir_path,
                                                enc_cfg_path = enc_cfg_path, quiet = quiet):
            return None

        cmd = EncFSCommands.build_ctl_show_info_cmd(encfs_dir_path = encfs_dir_path, enc_cfg_path = enc_cfg_path)
        try:
            output = run_cmd(cmd, shell = True)
        except CmdProcessingError as e:
            if not quiet:
                print ('Error while getting EncFS backend info: {}'.format(e.args[0]))
            return None
        else:
            return output

    @classmethod
    def key_info(cls, encfs_dir_path, enc_cfg_path, pwd = None, quiet = False):
        ''' EncFS key plaintext value
        '''
        # validate inputs
        key_info = None
        if not cls._check_args(encfs_dir_path = encfs_dir_path,
                                                enc_cfg_path = enc_cfg_path, quiet = quiet):
            return key_info

        with temp_dir() as tmp_encfs:
            target_path = os.path.join(tmp_encfs, EncFSCFG.DEFAULT_CFG_FNAME)
            shutil.copy(enc_cfg_path, target_path)
            cmd = EncFSCommands.build_ctl_show_key_cmd(encfs_dir_path = tmp_encfs)
            try:
                # if needed, temporarily reset the ENCFS6_CONFIG env variable
                encfs6_config_backup = cls._encfs6_config_backup_and_reset()

                output = EncFSCommands.expectant_pwd(cmd, pwd)
            except CmdProcessingError as e:
                if not quiet:
                    print ('Error while getting EncFS key value info: {}'.format(e.args[0]))
            else:
                key_info = cls._first_printable_line(output)
            finally:
                # if needed, restore the ENCFS6_CONFIG env variable
                cls._encfs6_config_restore(encfs6_config_backup)

        return key_info


    @classmethod
    def cruft_info(cls, encfs_dir_path, enc_cfg_path, target_cruft_path = None, pwd = None, quiet = False):
        ''' EncFS un-decodable filenames
        '''
        # validate inputs
        cruft_info = None
        if not cls._check_args(encfs_dir_path = encfs_dir_path,
                                                enc_cfg_path = enc_cfg_path, quiet = quiet):
            return cruft_info

        with temp_dir() as tmp_encfs:
            tmp_cruft_path = os.path.join(tmp_encfs, 'cruft')
            cmd = EncFSCommands.build_ctl_show_cruft_cmd(encfs_dir_path = encfs_dir_path,
                                                                    cruft_path = tmp_cruft_path)
            try:
                # if needed, temporarily reset the ENCFS6_CONFIG env variable
                encfs6_config_backup = cls._encfs6_config_backup_and_reset(enc_cfg_path)

                cruft_info = EncFSCommands.expectant_pwd(cmd, pwd).strip()
            except CmdProcessingError as e:
                if not quiet:
                    print ('Error while getting EncFS cruft info: {}'.format(e.args[0]))
            else:
                if tmp_cruft_path and target_cruft_path and os.path.exists(tmp_cruft_path):
                    shutil.copy(tmp_cruft_path, target_cruft_path)
            finally:
                # if needed, restore the ENCFS6_CONFIG env variable
                cls._encfs6_config_restore(encfs6_config_backup)

        return cruft_info.strip() if cruft_info else None

    @classmethod
    def encode(cls, encfs_dir_path, enc_cfg_path, filename, pwd, quiet = False):
        ''' Encodes file entry name
        '''
        # validate inputs
        if not cls._check_args(encfs_dir_path = encfs_dir_path,
                                                enc_cfg_path = enc_cfg_path, quiet = quiet):
            return None

        cmd = EncFSCommands.build_ctl_encode_cmd(encfs_dir_path = encfs_dir_path,
                                                            enc_cfg_path = enc_cfg_path,
                                                                    filename = filename, pwd = pwd)
        try:
            output = run_cmd(cmd, shell = True)
        except CmdProcessingError as e:
            if not quiet:
                print ('Error while encoding: {}'.format(e.args[0]))
            return None
        else:
            for encoded in output.splitlines():
                if encoded:
                    return encoded

        return None

    @classmethod
    def decode(cls, encfs_dir_path, enc_cfg_path, filename, pwd, quiet = False):
        ''' Decodes file entry name
        '''

        # validate inputs
        if not cls._check_args(encfs_dir_path = encfs_dir_path,
                                                enc_cfg_path = enc_cfg_path, quiet = quiet):
            return None
        cmd = EncFSCommands.build_ctl_decode_cmd(encfs_dir_path = encfs_dir_path,
                                                            enc_cfg_path = enc_cfg_path,
                                                                    filename = filename, pwd = pwd)
        try:
            output = run_cmd(cmd, shell = True)
        except CmdProcessingError as e:
            if not quiet:
                print ('Error while decoding: {}'.format(e.args[0]))
            return None
        else:
            for decoded in output.splitlines():
                if decoded:
                    return decoded

        return None

    # Helpers
    @staticmethod
    def _check_args(encfs_dir_path = None, enc_cfg_path = None, quiet = False):
        if enc_cfg_path and not (os.path.exists(enc_cfg_path) and os.path.isfile(enc_cfg_path)):
            if not quiet:
                print('Wrong conf/key path: {}'.format(enc_cfg_path))
            return False

        if encfs_dir_path and not (os.path.exists(encfs_dir_path) and os.path.isdir(encfs_dir_path)):
            if not quiet:
                print('Wrong backend folder path: {}'.format(encfs_dir_path))
            return False

        return True


    @staticmethod
    def _first_printable_line(lines):
        if not lines:
            return None
        else:
            for line in lines.splitlines():
                if (line):
                    return line

    @staticmethod
    def _encfs6_config_backup_and_reset(encfs6_config_new = None):
        encfs6_config_backup = None
        if os.environ.get(EncFSCFG.ENCFS_CONFIG):
            encfs6_config_backup = copy.copy(os.environ.get(EncFSCFG.ENCFS_CONFIG))

            if not encfs6_config_new:
                del os.environ[EncFSCFG.ENCFS_CONFIG]

        if encfs6_config_new:
            os.environ[EncFSCFG.ENCFS_CONFIG] = encfs6_config_new

        return encfs6_config_backup

    @staticmethod
    def _encfs6_config_restore(encfs6_config_backup):
        if encfs6_config_backup:
            os.environ[EncFSCFG.ENCFS_CONFIG] = encfs6_config_backup
        else:
            if os.environ.get(EncFSCFG.ENCFS_CONFIG):
                del os.environ[EncFSCFG.ENCFS_CONFIG]



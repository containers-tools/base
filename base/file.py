"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the MIT license. See the LICENSE file for details.
"""
import os
import shutil
import grp
import pwd

from cct.module import Module
from cct.lib.file_utils import create_dir

class File(Module):

    def copy(self, source, destination):
        """
        Copies file.

        Args:
            source: path to file
            destination: path where file should be copied
        """
        create_dir(destination)
        shutil.copy(source, destination)

    def link(self, source, destination):
        """
        Creates symbolik link.

        Args:
            source: path to symbolik link destination
            destination: Symbolik link name
        """
        create_dir(destination)
        os.symlink(source, destination)

    def move(self, source, destination):
        """
        Moves file.

        Args:
            source: path to file
            destination: path where file should be moved
        """
        create_dir(destination)
        shutil.move(source, destination)

    def remove(self, path):
        """
        Removes file.

        Args:
            source: path to file to be removed
        """
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)

    def chown(self, owner, group, path, recursive=False):
        """
        Change the ownership of a path.

        Args:
            owner: the owner (numeric or name) to change ownership to
            group: the group (numeric or name) to change groupship to
            path: the path to operate on
            recursive: if path is a directory, recursively change ownership for all
                       paths within
        """
        # supplied owner/group might be symbolic (e.g. 'wheel') or numeric.
        # Try interpreting symbolically first
        try:
            gid = grp.getgrnam(group).gr_gid
        except KeyError:
            gid = int(group,0)
        try:
            uid = pwd.getpwnam(owner).pw_uid
        except KeyError:
            uid = int(owner,0)

        # Beware: argument order is different
        os.chown(path, uid, gid)

        if recursive and os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for f in (dirnames + filenames):
                    os.chown(os.path.join(dirpath, f), uid, gid)

    def chmod(self, mode, path, recursive=False):
        """
        Change the permissions of a path.

        Args:
            path: the path to operate on
            mode: the numeric mode to set
            recursive: whether to change mode recursively
        """
        mode = int(mode,0)

        # Beware: argument order swapped
        os.chmod(path, mode)

        if recursive and os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for f in (dirnames + filenames):
                    os.chmod(os.path.join(dirpath, f), mode)

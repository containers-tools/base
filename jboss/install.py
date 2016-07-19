"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the MIT license. See the LICENSE file for details.
"""

from zipfile import ZipFile
from cct.module.jboss import JBossCliModule
from cct.lib.file_utils import chown, chmod
import os
import subprocess
import tempfile
import shutil

class JBossInstall(JBossCliModule):
    """
    This is a base module that can be extended to install JBoss EAP
    or WildFly application servers.

    Required modules:
        - JBossCliModule - https://github.com/containers-tools/base/tree/master/jboss

    Required software:
        - unzip

    Required env vars:
        - JBOSS_HOME - location where the distribution should be installed

    Required source keys:
        - distribution.zip - this is the binary distribution
    """

    def setup(self):
        self.jboss_home = os.getenv("JBOSS_HOME")

        if not self.jboss_home:
            raise Exception("JBOSS_HOME environment variable is not set, I don't know where to install the application server")

        self.sources_path = "/tmp/scripts/sources/"

    def teardown(self):
        # Do not execute teardown method from base class
        pass

    def _unpack_distribution(self):
        """ Extracts content of the distribution archive to JBOSS_HOME """

        distribution_zip_path = os.path.join(self.sources_path, self.artifacts['distribution.zip'].name)

        self.logger.info("Unpacking JBoss EAP distribution...")

        tmp_dir = tempfile.mkdtemp()

        ret = subprocess.call(["unzip", "-q", distribution_zip_path, "-d", tmp_dir])

        if ret is not 0:
            raise Exception("Couldn't unzip the %s file" % distribution_zip_path)

        # Main directory is always the first object in the archive
        zip = ZipFile(distribution_zip_path, 'r')
        distribution = zip.namelist()[0]

        # Move the distribution to the correct location
        shutil.move(os.path.join(tmp_dir, distribution), self.jboss_home)

        self.logger.debug("Unpacked!")

    def _apply_patches(self, patches):
        """
        Apply patches (if any) on top of the distribution using the
        CLI patch command
        """

        if not patches:
            self.logger.info("No patches to apply, skipping")
            return

        self.logger.info("Preparing to apply patches...")

        # Prepare to use CLI
        super(JBossInstall, self).setup()

        for patch in patches:
            self.logger.info("Applying %s patch" % patch)
            self.run_cli("patch apply %s" % os.path.join(self.sources_path, self.artifacts[patch].name))
            self.logger.info("Patch applied!")

        super(JBossInstall, self).teardown()

    def _change_owner(self):
        """ Makes sure the content is owned by appropriate user """

        self.logger.info("Changing distribution owner to 'jboss'...")

        chown(self.jboss_home, user="jboss", group="jboss", recursive=True)
        chmod(self.jboss_home, 0o755)

        self.logger.info("Owner changed")


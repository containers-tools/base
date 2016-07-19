"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the MIT license. See the LICENSE file for details.
"""

from zipfile import ZipFile
from cct.module import Module
from cct.lib.jboss_module import JBossCliModule
from cct.lib.file_utils import chown, chmod
import os
import logging
import subprocess
import tempfile
import shutil

logger = logging.getLogger('cct')

class JBossInstall(JBossCliModule):

    def setup(self):
        pass

    def teardown(self):
        pass

    def _unpack_distribution(self):
        jboss_home = os.getenv("JBOSS_HOME")

        if not jboss_home:
            raise("JBOSS_HOME environment variable is not set, I don't know where to install the application server")

        eap_zip_path = os.path.join("/tmp/scripts/sources/", self.artifacts['eap.zip'].name)

        logger.info("Unpacking JBoss EAP distribution...")

        tmp_dir = tempfile.mkdtemp()
        subprocess.call(["unzip", "-q", eap_zip_path, "-d", tmp_dir])

        zip = ZipFile(eap_zip_path, 'r')

        # Main directory is always the first object in the archive
        distribution = zip.namelist()[0]

        # Move the distribution to the correct location
        shutil.move(os.path.join(tmp_dir, distribution), os.getenv("JBOSS_HOME"))

        logger.debug("Unpacked!")

    def _apply_patches(self, patches):
        if not patches:
            logger.info("No patches to apply, skipping")
            return

        # Prepare to use CLI
        super(JBossInstall, self).setup()

        for patch in patches:
            logger.info("Applying %s patch" % patch)
            self.run_cli("patch apply %s" % os.path.join("/tmp/scripts/sources/", self.artifacts[patch].name))
            logger.info("Patch applied!")

        super(JBossInstall, self).teardown()

    def _change_owner(self):
        logger.debug("Changing distribution owner to jboss")

        chown(os.getenv("JBOSS_HOME"), user="jboss", group="jboss", recursive=True)
        chmod(os.getenv("JBOSS_HOME"), 0o755)


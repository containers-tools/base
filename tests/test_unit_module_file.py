import unittest
import mock
import tempfile
import shutil
import os
import stat

from base.file import File
from cct.errors import CCTError

class TestFileModule(unittest.TestCase):
    test_data = "Test Data 123"

    def setUp(self):
        self.tempdir = tempfile.mkdtemp('', 'test_unit_module_file')
        self.testfile = os.path.join(self.tempdir, "testfile")
        with open(self.testfile,'w') as fh:
            fh.write(self.test_data)

        self.ffile = File('shell', 'shell')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def _file_contains_test_data(self, f):
        with open(f, 'r') as fh:
            self.assertEqual(fh.read(), self.test_data)

    def test_copy(self):
        dest = os.path.join(self.tempdir, "dest")
        self.ffile.copy(self.testfile, dest)
        self._file_contains_test_data(dest)

    def test_link(self):
        dest = os.path.join(self.tempdir, "destlink")
        self.ffile.link(self.testfile, dest)
        self._file_contains_test_data(dest)

    def test_move(self):
        tmp   = os.path.join(self.tempdir, "tmpdest")
        final = os.path.join(self.tempdir, "finaldest")

        self.ffile.copy(self.testfile, tmp)
        self.ffile.move(tmp, final)

        self._file_contains_test_data(final)

    def test_remove(self):
        tmp = os.path.join(self.tempdir, "rmdest")
        self.ffile.copy(self.testfile, tmp)
        self.ffile.remove(tmp)
        self.assertFalse(os.path.exists(tmp))

    def test_removedir(self):
        tmp = os.path.join(self.tempdir, "rmdest")
        os.mkdir(tmp)
        self.ffile.remove(tmp)
        self.assertFalse(os.path.exists(tmp))

    def _test_chmod(self, modestr):
        self.ffile.chmod(modestr, self.testfile)
        mode = os.stat(self.testfile).st_mode

        desired = int(modestr, 0)
        actual = mode & (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        self.assertEqual(desired, actual)

    def test_chmod(self):
        """
        We run two separate tests with two different modes just in case
        the testfile happened to have the same mode as one test before
        chmod was called.
        """
        self._test_chmod("0666")
        self._test_chmod("0777")

if __name__ == '__main__':
    unittest.main()

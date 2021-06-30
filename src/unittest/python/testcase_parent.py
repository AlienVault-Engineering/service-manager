import os
import shutil
import tempfile
import unittest

from service_buddy_too.util import log_handler

DIRNAME = os.path.dirname(os.path.abspath(__file__))


class ParentTestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        try:
            shutil.rmtree(cls.temp_dir)
        except Exception as e:
            print('Error cleaning up ' +str(e))

    @classmethod
    def setUpClass(cls):
        super(ParentTestCase, cls).setUpClass()
        cls.service_directory = os.path.join(DIRNAME, '../resources/service_definition_test')
        cls.service_templates_test = os.path.join(DIRNAME, '../resources/service_templates_test/')
        cls.temp_dir = tempfile.mkdtemp()
        log_handler.configure_logging(True)

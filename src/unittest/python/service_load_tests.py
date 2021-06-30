import os

from service_buddy_too.service import loader
from service_buddy_too.util import pretty_printer
from testcase_parent import ParentTestCase

DIRNAME = os.path.dirname(os.path.abspath(__file__))


class ServiceLoadTestCase(ParentTestCase):


    @classmethod
    def setUpClass(cls):
        super(ServiceLoadTestCase, cls).setUpClass()

    def test_load_services(self):
        application_map = loader.load_service_definitions(self.service_directory, None)
        self.assertEqual(2, len(application_map), "Did not load all applications")
        app1 = application_map['app1']
        self.assertEqual(4, len(app1), "Did not load all services for app1")
        self._validate_service_definition(app1)
        app2 = application_map['app2']
        self.assertEqual(2, len(app2), "Did not load all services for app2")
        self._validate_service_definition(app2)
        pretty_printer.pretty_print_services(application_map)

    def test_app_filter(self):
        application_map = loader.load_service_definitions(self.service_directory,
                                                          code_directory=self.temp_dir,
                                                          app_filter='app1')
        self.assertEqual(1, len(application_map), "Did not load only app1")
        app1 = application_map['app1']
        self.assertEqual(4, len(app1), "Did not load all services for app1")
        self._validate_service_definition(app1)

    def _validate_service_definition(self, app):
        for key, value in app.items():
            self.assertTrue(value.get_service_type()is not None, "Did not load service type for {}".format(key))
            self.assertTrue(value.get_description() is not None, "Did not load service description for {}".format(key))
            self.assertTrue(value.get_repository_name() is not None, "Did not load service repo name for {}".format(key))
            self.assertTrue(value.repo_exists() is ("exists" in key), "Did not give rational response {}".format(key))

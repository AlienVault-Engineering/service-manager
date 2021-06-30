import json
import os

import testcase_parent
from service_buddy_too.service import loader
from service_buddy_too.service.initializer import Initializer
from service_buddy_too.service.service import Service
from service_buddy_too.util import command_util
from service_buddy_too.vcs.vcs import VCS
from testcase_parent import ParentTestCase


class InitTestCase(ParentTestCase):


    @classmethod
    def setUpClass(cls):
        super(InitTestCase, cls).setUpClass()
        command_util.dry_run_global = True
        cls.vcs = VCS(cls.service_directory)

    def validate_service_generation(self, definition):
        base_path = os.path.join(self.temp_dir, definition.get_app(), definition.get_fully_qualified_service_name())
        self.assertTrue(os.path.exists(os.path.join(base_path, "service/README.md")), "Did not find readme file")
        servicejson = os.path.join(base_path, "service/service.json")
        self.assertTrue(os.path.exists(servicejson), "Did not find service file")
        with open(servicejson) as fp:
            service = json.load(fp=fp)
            self.assertTrue('USE_FARGATE' in service['deployment-parameters'], "Failed to find defaults")

    def validate_generation(self, definition:Service):
        base_path = os.path.join(self.temp_dir, definition.get_app(), definition.get_fully_qualified_service_name())
        if "exists" in definition.get_fully_qualified_service_name():
            listdir = os.listdir(base_path)
            self.assertEqual(len(listdir),0, "Found code that should not exist - {}".format(base_path))
            return
        self.assertTrue(os.path.exists(base_path),
                        "Did not find generated code base - {}".format(definition.get_fully_qualified_service_name()))
        self.assertTrue(os.path.exists(os.path.join(base_path, "src")),
                        "Did not find generated code directory '{}/src' - {}".format(
                            base_path,
                            definition.get_fully_qualified_service_name()))
        self.assertTrue(os.path.exists(os.path.join(base_path, "build.py")), "Did not find generated build file")

    def test_project_init(self):
        command_util.dry_run_global = False
        application_map = loader.load_service_definitions(self.service_directory,code_directory=self.temp_dir)
        init = Initializer(vcs=self.vcs,
                           destination_directory=self.temp_dir,
                           code_template_directory=self.service_templates_test,
                           skip_git_creation=True)
        init.initialize_services(application_map)
        loader.walk_service_map(application_map, application_callback=None, service_callback=self.validate_generation)

    def test_service_definition_generation(self):
        init_test_dir = os.path.join(testcase_parent.DIRNAME, '../resources/initializer_test')
        application_map = loader.load_service_definitions(init_test_dir,code_directory=self.temp_dir)
        init = Initializer(vcs=self.vcs, destination_directory=self.temp_dir,
                           code_template_directory=init_test_dir,skip_git_creation=True)
        init.initialize_services(application_map)
        loader.walk_service_map(application_map, application_callback=None,
                                service_callback=self.validate_service_generation)

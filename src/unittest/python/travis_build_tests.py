import os
import shutil
from tempfile import mkdtemp

from service_buddy_too.ci.ci import BuildCreatorManager
from service_buddy_too.ci.travis_build_creator import TravisBuildCreator
from service_buddy_too.service import loader
from service_buddy_too.service.application import Application
from service_buddy_too.service.service import Service
from service_buddy_too.util import command_util
from testcase_parent import ParentTestCase

DIRNAME = os.path.dirname(os.path.abspath(__file__))


class TravisBuildTestCase(ParentTestCase):

    @classmethod
    def setUpClass(cls):
        super(TravisBuildTestCase, cls).setUpClass()
        cls.test_resources = os.path.join(DIRNAME, '../resources/travis_build_test')
        cls.yml_folder = os.path.join(cls.test_resources, "app1", "service")
        cls.app_dir = os.path.join(cls.test_resources, "app1")

    def test_travis_file_detection(self):
        command_util.dry_run_global = True
        build_creator = BuildCreatorManager(template_directory=self.test_resources)
        test_service = Service(app="app1", role="service", definition={"service-type": "test"},
                               app_reference=Application("app1", self.temp_dir))
        test_service.set_git_url("foobar")
        build_creator.create_project(service_definition=test_service)
        self._assertInYaml({"ubar": "Overwrote existing travis.yml"}, self.yml_folder)
        temp = mkdtemp()
        loader.safe_mkdir(test_service.get_service_directory())
        command_util.dry_run_global = False
        build_creator.create_project(service_definition=test_service)

    def test_travis_arg_render(self):
        items = "infra-buddy validate-template --service-template-directory . --service-type {role}"
        item2 = "pyb install_dependencies package -P build_number=0.1.${TRAVIS_BUILD_NUMBER}"
        list_args = []
        TravisBuildCreator._append_rendered_arguments(list_args, items, {'role': 'vbar'})
        self.assertTrue("vbar" in list_args[0], "Did not render properly")
        TravisBuildCreator._append_rendered_arguments(list_args, item2, {'role': 'vbar'})
        self.assertTrue("${TRAVIS_BUILD_NUMBER}" in list_args[1], "Did not render properly")

    def test_yml_update(self):
        command_util.dry_run_global = True
        temp = mkdtemp()
        source = os.path.join(self.yml_folder, '.travis.yml')
        destination = os.path.join(temp, '.travis.yml')
        shutil.copy(source, destination)
        build_creator = BuildCreatorManager(template_directory=self.test_resources)
        build_creator._get_default_build_creator()._write_deploy_stanza(temp)
        self._assertInYaml({"deploy": "Cound not find deploy stanza"}, temp)

    def _assertInList(self, param, line_list, error_message):
        for line in line_list:
            if param in line:
                return
        self.fail(error_message)

    def _assertInYaml(self, expected_error_msg, directory):
        destination = os.path.join(directory, '.travis.yml')
        with open(destination) as desty:
            readlines = desty.readlines()
            for expected, error_msg in expected_error_msg.items():
                self._assertInList(expected, readlines, error_msg)

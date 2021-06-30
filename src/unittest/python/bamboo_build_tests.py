import os

from service_buddy_too.ci.ci import BuildCreatorManager
from service_buddy_too.service.application import Application
from service_buddy_too.service.service import Service
from service_buddy_too.util import command_util
from testcase_parent import ParentTestCase

DIRNAME = os.path.dirname(os.path.abspath(__file__))


class BitbucketBuildTestCase(ParentTestCase):


    @classmethod
    def setUpClass(cls):
        super(BitbucketBuildTestCase, cls).setUpClass()
        cls.test_resources = os.path.join(DIRNAME, '../resources/bamboo_build_test')

    def test_bitbucket_build_creation(self):
        command_util.dry_run_global = True
        build_creator = BuildCreatorManager(template_directory=self.test_resources)
        test_service = Service(app="app1",
                               role="service",
                               definition={"service-type": "test"},
                               app_reference=Application("app1",self.temp_dir))
        test_service.set_git_url("git@github.com:rspitler/service-buddy-tests.git")
        build_creator.create_project(service_definition=test_service)

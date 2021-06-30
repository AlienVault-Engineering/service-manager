import os

from service_buddy_too.service import loader
from service_buddy_too.util import command_util
from service_buddy_too.vcs.bitbucket import BitbucketVCSProvider
from service_buddy_too.vcs.vcs import VCS, vcs_provider_map
from testcase_parent import ParentTestCase

DIRNAME = os.path.dirname(os.path.abspath(__file__))


class VCSTestCase(ParentTestCase):

    @classmethod
    def setUpClass(cls):
        super(VCSTestCase, cls).setUpClass()
        cls.bad_vcs = os.path.join(DIRNAME, 'resources/bad_vcs')

    def test_vcs_init(self):
        try:
            vcs = VCS(self.bad_vcs)
            self.fail("Did not except")
        except Exception as exc:
            self.assertTrue("vcs-config.json" in str(exc))
        vcs = VCS(self.service_directory)
        self.assertTrue(vcs.default_provider == "bitbucket", "Failed to load default provider")
        self.assertTrue(type(vcs_provider_map[vcs.default_provider]) == BitbucketVCSProvider,
                        "Failed to load default provider")
        application_map = loader.load_service_definitions(self.service_directory,code_directory=self.temp_dir)
        vcs.validate_repositories(application_map=application_map)
        vcs.clone_service(application_map=application_map)
        command_util.dry_run_global = True
        for key, app in application_map.items():
            for key, service in app.items():
                vcs.init_repo(service)

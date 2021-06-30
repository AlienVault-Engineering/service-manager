import os

import testcase_parent
from service_buddy_too.service import loader
from service_buddy_too.util import command_util
from service_buddy_too.vcs.github_vcs import GitHubVCSProvider
from testcase_parent import ParentTestCase


class TestGitHubClient(object):

    def __init__(self, application_map):
        super(TestGitHubClient, self).__init__()
        self.known_repos = []
        for app in application_map.values():
            self.known_repos.extend([RepoReturn(definition.get_repository_name())for definition in app.values()])

    def get_repos(self):
        return self.known_repos

    def create_repo(self,name,private,has_issues,description,has_projects,has_wiki):
        return RepoReturn(repository_name=name)

class RepoReturn(object):
    def __init__(self, repository_name):
        super(RepoReturn, self).__init__()
        self.name = "test/{}".format(repository_name)
        self.ssh_url = "ssh://git@bitbucket.org/{}".format(repository_name)


class GitHubVCSInitTest(ParentTestCase):


    @classmethod
    def setUpClass(cls):
        super(GitHubVCSInitTest, cls).setUpClass()
        cls.vcs = GitHubVCSProvider()
        cls.github_test_dir = os.path.join(testcase_parent.DIRNAME, '../resources/github_repo_tests')
        cls.vcs.init(None, None, "rspitler")

    def validate_exists(self,service_definition):
        repo = self.vcs.find_repo(service_definition)
        self.assertIsNotNone(repo,"Failed to find repo")

    def validate_create(self,service_definition):
        repo = self.vcs.create_repo(service_definition)
        self.assertIsNotNone(repo,"Failed to create repo")

    def test_repo_exists(self):
        command_util.dry_run_global = False
        self.vcs.client = None
        application_map = loader.load_service_definitions(self.github_test_dir,code_directory=self.temp_dir)
        loader.walk_service_map(application_map, application_callback=None, service_callback=self.validate_exists)

    def test_repo_create(self):
        application_map = loader.load_service_definitions(self.service_directory,code_directory=self.temp_dir)
        self.vcs.client = TestGitHubClient(application_map)
        command_util.dry_run_global = False
        loader.walk_service_map(application_map, application_callback=None, service_callback=self.validate_create)


import logging

from github import Github
from requests import HTTPError

from service_buddy_too.util import command_util
from service_buddy_too.util.command_util import invoke_process


class GitHubVCSProvider(object):
    @classmethod
    def get_type(cls):
        return 'github'


    def __init__(self, ):
        super(GitHubVCSProvider, self).__init__()
        self.repo_root = ""
        self.client = None

    def init(self, user, password, repo_root):
        self.repo_root = repo_root
        if user and password:
            self.client = Github(user, password).get_organization(self.repo_root)
        else:
            logging.warning(
                "VCS username and password not configured - assuming git executable has appropriate authorization for "
                "repo checks")
            self.client = None

    def find_repo(self, service_definition):
        fq_repository_name = "{}/{}".format(self.repo_root, service_definition.get_repository_name())
        try:
            if self.client:
                ssh_url = None
                for repo in self.client.get_repos():
                    if repo.name == fq_repository_name:
                        ssh_url = repo.ssh_url
                        break
            else:
                ssh_url = 'https://git@github.com/{}.git'.format(fq_repository_name)
                result = invoke_process(args=['git', 'ls-remote', ssh_url, '>', '/dev/null'], exec_dir=None)
                if result != 0:
                    logging.info("Could not find repository with git executable - {}".format(
                        service_definition.get_repository_name()))
                    ssh_url = None
            return ssh_url
        except HTTPError:
            logging.info("Could not find repository through github API - {}".format(service_definition.get_repository_name()))

    def create_repo(self, service_defintion):
        # name, description=github.GithubObject.NotSet,
        #  private=github.GithubObject.NotSet,
        # has_issues=github.GithubObject.NotSet,
        # has_wiki=github.GithubObject.NotSet,
        # has_downloads=github.GithubObject.NotSet,
        # team_id=github.GithubObject.NotSet,
        # gitignore_template=github.GithubObject.NotSet
        payload = {
            "name": service_defintion.get_fully_qualified_service_name(),
            "description": service_defintion.get_description(),
            "private": True,
            "has_issues": False,
            "has_projects": False,
            "has_wiki": False
        }
        if command_util.dry_run_global:
            logging.error("Creating repo {}".format(str(payload)))
        else:
            if self.client is None:
                raise Exception("VCS pass required for create repo operation")
            repo = self.client.create_repo(**payload)
            return repo.ssh_url

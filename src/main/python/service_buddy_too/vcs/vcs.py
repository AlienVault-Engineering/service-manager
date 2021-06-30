import json
import logging
import os
from collections import OrderedDict
from typing import Dict, Union

from service_buddy_too.service.loader import walk_service_map
from service_buddy_too.service.service import Service
from service_buddy_too.util.command_util import invoke_process
from service_buddy_too.vcs.bitbucket import BitbucketVCSProvider
from service_buddy_too.vcs.github_vcs import GitHubVCSProvider

vcs_provider_map: Dict[str, Union[BitbucketVCSProvider, GitHubVCSProvider]] = {
    BitbucketVCSProvider.get_type(): BitbucketVCSProvider(),
    GitHubVCSProvider.get_type(): GitHubVCSProvider()}
vcs_providers = [key for key in vcs_provider_map.keys()]

options = OrderedDict()
options['root-user'] = "Organization name. Team name, organization, workspace or root user used by vcs provider"
options['user'] = "Username for authentication when creating repositories (leave blank to use ${VCS_USER})"
options['password'] = "Password for authentication when creating repositories (leave blank to use ${VCS_PASSWORD})"


class VCS(object):
    def __init__(self, service_directory):
        super(VCS, self).__init__()
        default_path = os.path.join(service_directory, "vcs-config.json")
        if os.path.exists(default_path):
            with open(default_path) as fp:
                defaults = json.load(fp)
                self.default_provider = defaults.get('provider', None)
                self.repo_root = defaults.get('root-user', os.environ.get('VCS_ROOT_USER'))
                self.user = defaults.get('user', os.environ.get('VCS_USER'))
                self.password = defaults.get('password', os.environ.get('VCS_PASSWORD'))
        else:
            raise Exception("Could not local 'vcs-config.json' in service directory")
        if self.default_provider not in vcs_provider_map:
            raise Exception("Requested provider is not configured {}".format(self.default_provider))
        else:
            self._get_default_vcs_provider().init(self.user, self.password, self.repo_root)

    def _get_default_vcs_provider(self):
        return vcs_provider_map[self.default_provider]

    def validate_repositories(self, application_map):
        def populate_repo_metadata(service_definition):
            repo_url = self._get_default_vcs_provider().find_repo(service_definition)
            service_definition.set_git_url(repo_url)

        walk_service_map(application_map=application_map, application_callback=None,
                         service_callback=populate_repo_metadata)

    def create_project(self, service_definition, app_dir=None):
        return self.init_repo(service_definition=service_definition)

    def init_repo(self, service_definition:Service):
        repo_url = self._get_default_vcs_provider().create_repo(service_definition)
        self.init_git_for_directory(repo_url, service_definition.get_service_directory())
        self.perform_initial_commit(service_definition.get_service_directory())
        service_definition.set_git_url(repo_url)

    def init_git_for_directory(self, repo_url, service_dir):
        args = ['git', 'init']
        invoke_process(args, exec_dir=service_dir)
        args = ['git', 'remote', 'add', 'origin', repo_url]
        invoke_process(args, exec_dir=service_dir)

    def perform_initial_commit(self, service_dir):
        args = ['git', 'add', '*', '**/*']
        invoke_process(args, exec_dir=service_dir)
        args = ['git', 'commit', '-m', 'Initial commit']
        invoke_process(args, exec_dir=service_dir)
        args = ['git', 'push', '-u', 'origin', 'master']
        invoke_process(args, exec_dir=service_dir)

    def clone_service(self, application_map):

        def clone_repository(service_defintion:Service):
            service_defintion.clone_repo()

        walk_service_map(application_map=application_map, application_callback=None,
                         service_callback=clone_repository)

    def git_exec(self, application_map, destination_directory, args):
        # type: (dict,str, list) -> None

        def git_exec(service_defintion):
            # type: (Service) -> None
            destination_dir = service_defintion.get_service_directory()
            if not destination_directory:
                logging.warning("Service '{}' did not exist in destination directory - {}".format(
                    service_defintion.get_fully_qualified_service_name(), destination_directory))
                logging.warning("Skipping running git command - git {}".format(str(args)))
                return
            logging.warning("Invoking git in directory - '{}' ".format(destination_dir))
            git_args = ['git']
            git_args.extend(args)
            invoke_process(git_args, destination_dir)

        walk_service_map(application_map=application_map, application_callback=None,
                         service_callback=git_exec)

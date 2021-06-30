import logging
import os

from service_buddy_too.service.application import Application
from service_buddy_too.util.command_util import invoke_process

REPO_URL = 'repository_url'

REPOSITORY_NAME = 'repository'
REPOSITORY_URL = 'repository_url'
DESCRIPTION = 'description'
ROLE = 'role'
APPLICATION = 'application'
FQN = 'project_name'
FORCE_RECREATE_BUILD = 'recreate-build'
SERVICE_TYPE = 'service-type'


class Service(dict):
    def __init__(self, app:str, role:str, definition:dict, app_reference:Application):
        super(Service, self).__init__()
        self.update(definition)
        self.app_ref = app_reference
        self[APPLICATION] = app
        self[ROLE] = role
        self[FQN] = self.get_fully_qualified_service_name()

    def get_fully_qualified_service_name(self):
        return "{application}-{role}".format(**self).replace(' ','_')

    def force_recreate_build(self):
        return self.get(FORCE_RECREATE_BUILD,os.environ.get('RECREATE_BUILDS',False))

    def get_description(self):
        return self[DESCRIPTION]

    def get_service_type(self):
        return self[SERVICE_TYPE]

    def repo_exists(self):
        return self.get(REPOSITORY_URL,None) is not None

    def get_role(self):
        return self[ROLE]

    def get_app(self):
        return self[APPLICATION]

    def get_repository_name(self):
        return self[REPOSITORY_NAME] if REPOSITORY_NAME in self else self.get_fully_qualified_service_name()

    def set_git_url(self, url):
        self[REPO_URL] = url

    def get_git_url(self):
        return self.get(REPO_URL,None)

    def get_service_directory(self):
        join = os.path.join(self.get_parent_dir(), self.get_role())
        os.makedirs(join, exist_ok=True)
        return join

    def get_parent_dir(self):
        directory = self.app_ref.get_app_code_directory()
        os.makedirs(directory, exist_ok=True)
        return directory

    def is_service_directory_configured_for_git(self) -> bool:
        service_dir = self.get_service_directory()
        return '.git' in os.listdir(service_dir)

    def set_service_type(self, param):
        self[SERVICE_TYPE] = param

    def clone_repo(self):
        if not  self.repo_exists(): raise Exception("Repository URL not configured before calling prep_git")
        repo_url = self.get_git_url()
        args = ['git', 'clone', repo_url, self.get_role()]
        if self.is_service_directory_configured_for_git():
            logging.info("Directory already configured for git - {}".format(self.get_service_directory()))
        else:
            parent_dir = self.get_parent_dir()
            logging.warning(f"Cloning repo from git for local modification - {repo_url} - {parent_dir}")
            invoke_process(args, parent_dir)
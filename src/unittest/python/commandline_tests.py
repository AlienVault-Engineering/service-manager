import json
import os

import click

from click.testing import CliRunner

from service_buddy_too.commandline import cli
from service_buddy_too.context.service_context import ServiceContext
from testcase_parent import ParentTestCase

ctx = None


@cli.command(name='test-command')
@click.pass_obj
def test_method(service_ctx):
    # type: (ServiceContext) -> None
    global ctx
    ctx = service_ctx


class CommandlineTestCase(ParentTestCase):


    @classmethod
    def setUpClass(cls):
        super(CommandlineTestCase, cls).setUpClass()

    def test_context_creation(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--service-directory', self.service_directory, '--dry-run', 'test-command'])
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout}")
        self.assertTrue(ctx.vcs, "Failed to init vcs")
        self.assertTrue(ctx.application_map, "Failed to init app map")

    def test_boostrap(self):
        runner = CliRunner()
        vcs_provider = "bitbucket"
        vcs_root_user = "foo_root"
        vcs_user_name = "root_un"
        vcs_pass = "root_pass"
        build_provider = "bamboo"
        build_url = "https://bamboo.atlassian.net"
        vcs_root_user = "foo_root"
        build_user_name = "root_un"
        build_pass = "build_pass"
        cli_input = [
            vcs_provider,  # vcs provider
            vcs_root_user,  # vcs_root_user
            vcs_user_name,  # vcs user name
            vcs_pass,  # vcs pass
            build_provider,  # build_system_provider
            build_url,  # build_system_url
            build_user_name,
            build_pass
        ]
        result = runner.invoke(cli, ['--destination-directory',
                                     self.temp_dir, 'bootstrap', '--application', 'app'], input='\n'.join(cli_input))
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout}")
        root_dir = os.path.join(self.temp_dir, "app-master")
        self.assertTrue(os.path.exists(root_dir), "Failed to create dir")
        code_template_dir = os.path.join(root_dir, "code-templates")
        self.assertTrue(os.path.exists(code_template_dir), "Failed to create code-templates")
        build_config_file = os.path.join(code_template_dir, 'build-config.json')
        with open(build_config_file) as build_config_fp:
            build_config = json.load(build_config_fp)
            self.assertEqual(build_config['provider'], build_provider)
            self.assertEqual(build_config['url'], build_url)
            self.assertEqual(build_config['user'], build_user_name)
            self.assertEqual(build_config['password'], build_pass)
        service_dir = os.path.join(root_dir, "services")
        self.assertTrue(os.path.exists(service_dir), "Failed to create services")
        vcs_config_file = os.path.join(service_dir, "vcs-config.json")
        with open(vcs_config_file) as vcs_config_fp:
            vcs_config = json.load(vcs_config_fp)
            self.assertEqual(vcs_config['provider'], vcs_provider)
            self.assertEqual(vcs_config['root-user'], vcs_root_user)
            self.assertEqual(vcs_config['user'], vcs_user_name)
            self.assertEqual(vcs_config['password'], vcs_pass)
        self.assertTrue(os.path.exists(os.path.join(service_dir, 'app')), "Failed to create app directory")


    def test_list(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--service-directory', self.service_directory, '--dry-run', 'list'])
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout}")


    def test_clone(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--service-directory',
                                     self.service_directory,
                                     '--dry-run',
                                     '--destination-directory',
                                     self.temp_dir,
                                     'clone'
                                     ])
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout}")



    def test_git(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--service-directory',
                                     self.service_directory,
                                     '--dry-run',
                                     '--destination-directory',
                                     self.temp_dir,
                                     'git',
                                     "foo"])
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout}")



    def test_init(self):
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--service-directory',
            self.service_directory,
            '--dry-run',
            '--destination-directory',
            self.temp_dir,
            'init',
            '--code-template-definitions',
            self.service_templates_test
        ]
                               )
        self.assertEqual(result.exit_code, 0, f"Did not get good exit code: {result.stdout}")


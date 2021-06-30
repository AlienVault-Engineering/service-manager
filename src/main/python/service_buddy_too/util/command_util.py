import logging
import subprocess

from service_buddy_too.util.log_handler import print_red_bold

dry_run_global = False

def invoke_process(args, exec_dir=None):
    if dry_run_global:
        print_red_bold(u"\t {}".format(str(args)))
        return 0
    else:
        arg_list = {'args': args}
        arg_list['stderr'] = subprocess.STDOUT
        if exec_dir:
            arg_list['cwd'] = exec_dir

        logging.debug(u'[exec] invoke_process args=%r, exec_dir=%r, dry_run=%r', args, exec_dir, dry_run_global)
        returncode = 0
        try:
            output = subprocess.check_output(**arg_list)
        except subprocess.CalledProcessError as e:
            output = e.output
            returncode = e.returncode

        for line in output.splitlines():
            logging.debug(u'[exec] %s', line)
        logging.debug(u'[exec] invoke_process complete args=%r, exec_dir=%r, dry_run=%r', args, exec_dir, dry_run_global)

        return returncode

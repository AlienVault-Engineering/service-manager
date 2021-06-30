from service_buddy_too.util import command_util
from testcase_parent import ParentTestCase



class CommandUtilityTestCase(ParentTestCase):


    @classmethod
    def setUpClass(cls):
        super(CommandUtilityTestCase, cls).setUpClass()

    def test_invoke(self):
        return_code = command_util.invoke_process(["echo", "foo",'>','/dev/null'])
        self.assertEqual(return_code,0,"Did not invoke trivial process")


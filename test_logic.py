import unittest

from logic import make_status


class TestLogic(unittest.TestCase):

    def test_status_is_ok(self):
        result = make_status()

        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["service"], "jenkins-ci-demo")


if __name__ == "__main__":
    unittest.main()

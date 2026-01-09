import unittest
from uvlisk.main import resolve_uv_version

class TestResolveUvVersion(unittest.TestCase):
    def test_simple_version(self):
        self.assertEqual(resolve_uv_version("0.5.0"), "0.5.0")
        self.assertEqual(resolve_uv_version("0.5"), "0.5")

    def test_latest(self):
        self.assertEqual(resolve_uv_version("latest"), "latest")
        self.assertEqual(resolve_uv_version(""), "latest")

    def test_constraints(self):
        self.assertEqual(resolve_uv_version(">=0.8"), "latest")
        self.assertEqual(resolve_uv_version("<0.8"), "latest")
        self.assertEqual(resolve_uv_version("~=0.5.0"), "latest")
        self.assertEqual(resolve_uv_version("!=0.5.0"), "latest")
        self.assertEqual(resolve_uv_version("0.5.*"), "latest")
        self.assertEqual(resolve_uv_version(">=0.5, <0.6"), "latest")

    def test_pinned_equality(self):
        self.assertEqual(resolve_uv_version("==0.5.0"), "0.5.0")
        self.assertEqual(resolve_uv_version("== 0.5.0"), "0.5.0")

    def test_complex_equality(self):
        self.assertEqual(resolve_uv_version("===0.5.0"), "latest")

    def test_caret(self):
        self.assertEqual(resolve_uv_version("^0.5.0"), "latest")

if __name__ == "__main__":
    unittest.main()

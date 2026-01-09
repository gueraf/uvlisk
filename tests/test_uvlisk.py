import unittest
from uvlisk.main import resolve_uv_version

class TestResolveUvVersion(unittest.TestCase):
    def test_simple_version(self):
        self.assertEqual(resolve_uv_version("0.5.0"), "0.5.0")
        self.assertEqual(resolve_uv_version("0.5"), "0.5")

    def test_latest(self):
        self.assertEqual(resolve_uv_version("latest"), "latest")
        self.assertEqual(resolve_uv_version(""), "latest")

    def test_inclusive_constraints(self):
        self.assertEqual(resolve_uv_version(">=0.8"), "0.8")
        self.assertEqual(resolve_uv_version("<=0.8"), "0.8")

    def test_pinned_equality(self):
        self.assertEqual(resolve_uv_version("==0.5.0"), "0.5.0")
        self.assertEqual(resolve_uv_version("== 0.5.0"), "0.5.0")

    def test_unsupported_constraints(self):
        with self.assertRaises(ValueError):
            resolve_uv_version("<0.8")
        with self.assertRaises(ValueError):
            resolve_uv_version(">0.8")
        with self.assertRaises(ValueError):
            resolve_uv_version("~=0.5.0")
        with self.assertRaises(ValueError):
            resolve_uv_version("!=0.5.0")
        with self.assertRaises(ValueError):
            resolve_uv_version("^0.5.0")
        with self.assertRaises(ValueError):
            resolve_uv_version("0.5.*")
        with self.assertRaises(ValueError):
            resolve_uv_version(">=0.5, <0.6")
        with self.assertRaises(ValueError):
            resolve_uv_version("===0.5.0")

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/python
import unittest
import sys

sys.path.insert(0, '.')

if __name__ == "__main__":
    all_tests = unittest.TestLoader().discover('./tests/')
    unittest.TextTestRunner().run(all_tests)

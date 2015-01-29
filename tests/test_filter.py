import unittest
from umea.search import F, Search, filterbuilder, FILTER_PATTERN

class LdapFilterPatternSimpleMatch(unittest.TestCase):
    def setUp(self):
        self.pattern = FILTER_PATTERN

    def test_match_letters(self):
        attribute = "givenname"
        match = self.pattern.match(attribute)
        self.assertEqual(match.group('attribute'), attribute)

    def test_match_mixed_case_letters(self):
        attribute = "GivenName"
        match = self.pattern.match(attribute)
        self.assertEqual(match.group('attribute'), attribute)

    def test_match_numbers(self):
        attribute = "012141451"
        match = self.pattern.match(attribute)
        self.assertEqual(match.group('attribute'), attribute)

    def test_match_letters_and_numbers(self):
        attribute = "abcABs10291"
        match = self.pattern.match(attribute)
        self.assertEqual(match.group('attribute'), attribute)

    def test_not_match_chars(self):
        attribute = "givenname--"
        match = self.pattern.match(attribute)
        self.assertIsNone(match)


class LdapFilterPatternExtendedMatch(unittest.TestCase):
    def setUp(self):
        self.pattern = FILTER_PATTERN

    def test_match_ne(self):
        attribute = "givenname__ne"
        match = self.pattern.match(attribute)
        attribute, extended, separator, negate, operation, _ = match.groups()
        self.assertEqual(attribute, 'givenname')
        self.assertEqual(extended, '__ne')
        self.assertIsNone(negate)
        self.assertEqual(separator, '__')
        self.assertEqual(operation, 'ne')

    def test_match_startswith(self):
        attribute = "givenname__startswith"
        match = self.pattern.match(attribute)
        attribute, extended, separator, negate, operation, _ = match.groups()
        self.assertEqual(attribute, 'givenname')
        self.assertEqual(extended, '__startswith')
        self.assertIsNone(negate)
        self.assertEqual(separator, '__')
        self.assertEqual(operation, 'startswith')

    def test_match_negate(self):
        attribute = "givenname__not_startswith"
        match = self.pattern.match(attribute)
        attribute, extended, separator, negate, operation, _ = match.groups()
        self.assertEqual(attribute, 'givenname')
        self.assertEqual(extended, '__not_startswith')
        self.assertEqual(negate, 'not_')
        self.assertEqual(separator, '__')
        self.assertEqual(operation, 'startswith')

    def test_not_match_just_negate(self):
        attribute = "givenname__not_"
        match = self.pattern.match(attribute)
        self.assertIsNone(match)

    def test_not_match_just_separator(self):
        attribute = "givenname__"
        match = self.pattern.match(attribute)
        self.assertIsNone(match)


class LdapFilterFFunction(unittest.TestCase):

    def test_equal(self):
        self.assertEqual("orange=color", str(F(orange="color")))

    def test_not_equal(self):
        self.assertEqual("!(orange=color)", str(~F(orange="color")))

    def test_and(self):
        self.assertEqual("&(orange=color)(orange=fruit)", str(F(orange="color") & F(orange="fruit")))

    def test_or(self):
        self.assertEqual("|(orange=color)(orange=fruit)", str(F(orange="color") | F(orange="fruit")))

    def test_from_string(self):
        self.assertEqual("|(orange=color)(orange=fruit)", str(F.from_string("|(orange=color)(orange=fruit)")))


class LdapFilterFilterBuilder(unittest.TestCase):
    
    def test_args(self):
        self.assertEqual(str(F(apple="fruit")), str(filterbuilder(F(apple="fruit"))))

    def test_multiple_args(self):
        self.assertEqual(str(F(apple="fruit") & F(apple="round")), str(filterbuilder(F(apple="fruit"), F(apple="round"))))

    def test_kwargs(self):
        self.assertEqual(str(F(apple="fruit")), str(filterbuilder(apple="fruit")))

    def test_args_and_kwargs(self):
        self.assertEqual(str(F(apple="fruit") & F(earth="round")), str(filterbuilder(F(apple="fruit"), earth="round")))







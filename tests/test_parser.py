from unittest import TestCase
from cron import parse, Range, NumericParser, MonthParser, WeekdayParser, CronException


class TestParser(TestCase):

    def test_NumericParser_with_empty_string(self):
        result = NumericParser(Range(0, 20)).parse_argument("")
        self.assertEqual([], result)

    def test_NumericParser_handles_comas(self):
        expected = [10, 11, 12, 13]
        actual = NumericParser(Range(0, 23)).parse_argument("10,11,12,13")
        self.assertEqual(expected, actual)

    def test_NumericParser_using_comas_with_numbers_outside_of_range(self):
        expected = [11, 12, 13]
        actual = NumericParser(Range(11, 13)).parse_argument("10,11,12,13,14")
        self.assertEqual(expected, actual)

    def test_NumericParser_using_comas_with_numbers_not_in_the_range(self):
        expected = []
        actual = NumericParser(Range(6, 9)).parse_argument("1,2,3,4,5")
        self.assertEqual(expected, actual)

    def test_NumericParser_handles_hyphen_ranges(self):
        expected = [0, 1, 2, 3, 4, 5]
        actual = NumericParser(Range(0, 23)).parse_argument("0-5")
        self.assertEqual(expected, actual)

    def test_NumericParser_using_hyphen_range_with_some_numbers_outside_of_range(self):
        expected = [1, 2, 3]
        actual = NumericParser(Range(1, 3)).parse_argument("0-5")
        self.assertEqual(expected, actual)

    def test_NumericParser_using_hyphen_range_with_all_the_numbers_outside_of_range_Returns_empty_list(self):
        expected = []
        actual = NumericParser(Range(1, 3)).parse_argument("5-10")
        self.assertEqual(expected, actual)

    def test_NumericParser_using_hyphen_range_that_allows_only_one_number(self):
        expected = [5]
        actual = NumericParser(Range(5, 5)).parse_argument("4-6")
        self.assertEqual(expected, actual)

    def test_NumericParser_using_hyphen_range_with_reversed_min_max_values_of_range_Returns_empty_list(self):
        expected = []
        actual = NumericParser(Range(1, 3)).parse_argument("10-5")
        self.assertEqual(expected, actual)

    def test_NumericParser_using_stepped_hyphen_range(self):
        expected = [10, 12, 14, 16, 18, 20]
        actual = NumericParser(Range(1, 22)).parse_argument("10-20/2")
        self.assertEqual(expected, actual)

    def test_NumericParser_using_stepped_hyphen_range_with_last_step_overstepping_the_max_in_range(self):
        expected = [10, 12, 14, 16, 18]
        actual = NumericParser(Range(1, 22)).parse_argument("10-19/2")
        self.assertEqual(expected, actual)

    def test_NumericParser_using_stepped_asterisk_range(self):
        expected = [0, 3, 6, 9]
        actual = NumericParser(Range(0, 9)).parse_argument("*/3")
        self.assertEqual(expected, actual)

    def test_NumericParser_combine_coma_list_with_stepped_hyphen_range_with_no_overlap(self):
        expected = [1, 2, 4, 6, 8, 22]
        actual = NumericParser(Range(0, 23)).parse_argument("1,2,22,4-9/2")
        self.assertEqual(expected, actual)

    def test_NumericParser_combine_using_hyphen_range_with_words_for_month(self):
        expected = [1, 2, 4, 6, 8, 22]
        actual = NumericParser(Range(0, 23)).parse_argument("1,2,22,4-9/2")
        self.assertEqual(expected, actual)

########################################################################################################################

    def test_MonthParser_ranges_from_1_to_12_using_asterisk(self):
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        actual = MonthParser().parse_argument("*")
        self.assertEqual(expected, actual)

    def test_MonthParser_with_word_month_range_using_hyphen(self):
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        actual = MonthParser().parse_argument("jan-oct")
        self.assertEqual(expected, actual)

    def test_MonthParser_is_case_insensitive(self):
        expected = [1, 2, 3, 10, 11, 12]
        actual = MonthParser().parse_argument("Jan,fEb,MAR,ocT,NoV,dec")
        self.assertEqual(expected, actual)

    def test_MonthParser_handles_mixed_numeric_and_word_values(self):
        expected = [1, 2, 3, 4, 5, 6, 10, 11, 12]
        actual = MonthParser().parse_argument("Jan,2,MAR,4-6,ocT-dec")
        self.assertEqual(expected, actual)

    def test_MonthParser_handles_stepped_range_using_words_as_months(self):
        expected = [2, 5, 8]
        actual = MonthParser().parse_argument("feb-oct/3")
        self.assertEqual(expected, actual)

    def test_MonthParser_raises_exception_if_invalid_value_is_used(self):
        with self.assertRaises(CronException):
            MonthParser().parse_argument("feb-car/3")

########################################################################################################################

    def test_WeekdayParser_ranges_from_1_to_7_using_asterisk(self):
        expected = [1, 2, 3, 4, 5, 6, 7]
        actual = WeekdayParser().parse_argument("*")
        self.assertEqual(expected, actual)

    def test_WeekdayParser_with_word_range_using_hyphen(self):
        expected = [2, 3, 4, 5]
        actual = WeekdayParser().parse_argument("tue-fri")
        self.assertEqual(expected, actual)

    def test_WeekdayParser_is_case_insensitive(self):
        expected = [1, 2, 3, 4, 5, 6, 7]
        actual = WeekdayParser().parse_argument("Mon,tUe,weD,ThU,FRI,SAt,sUN")
        self.assertEqual(expected, actual)

    def test_WeekdayParser_handles_mixed_numeric_and_word_values(self):
        expected = [1, 2, 3, 4, 5, 6, 7]
        actual = WeekdayParser().parse_argument("mon,2,3-4,fri-sun")
        self.assertEqual(expected, actual)

    def test_WeekdayParser_handles_stepped_range_using_words_as_days(self):
        expected = [1, 3, 5, 7]
        actual = WeekdayParser().parse_argument("mon-sun/2")
        self.assertEqual(expected, actual)

    def test_WeekdayParser_raises_exception_if_invalid_value_is_used(self):
        with self.assertRaises(CronException):
            MonthParser().parse_argument("mon,may")

    def test_missing_arguments_is_handled(self):
        result = parse("1 2 3 4")
        self.assertEqual(1, len(result))
        self.assertTrue(result[0].startswith("Invalid number of arguments"))

    def test_too_many_arguments_is_handled(self):
        result = parse("1 2 3 4 5 my/command 6")
        self.assertEqual(1, len(result))
        self.assertTrue(result[0].startswith("Invalid number of arguments"))

    def test_all(self):
        expected = ["minute         0 15 30 45",
                    "hour           12 14 16 18 20",
                    "day of month   1 2 3 10 15 20 25",
                    "month          1 10 11 12",
                    "day of week    1 2 3 4 5 6",
                    "command        my/command"]
        actual = parse("*/15 12-20/2 1,2,3,10-25/5 jan,10-12/1 1,tue-6 my/command")
        self.assertEqual(expected, actual)

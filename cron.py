import sys
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict
from copy import copy


class Range:
    def __init__(self, min_val: int, max_val: int):
        self.min = min_val
        self.max = max_val


class CronException(Exception):
    pass


class ArgumentParser(ABC):

    def __init__(self, value_range: Range):
        self._value_range: Range = value_range

    def parse_argument(self, argument: str) -> List[int]:
        all_values = []
        value_range = self._value_range
        value, pos = self._next_value(argument, len(argument) - 1)

        while pos >= 0:
            symbol = argument[pos]
            if symbol == '/':
                values, pos = self._read_range(argument, pos - 1)
                step = self.parse_value(value)
                all_values.extend([val for val in range(values[0], values[-1] + 1, step)])

            elif symbol == ',':
                all_values.append(self.parse_value(value))

            elif symbol == '-':
                min_value, pos = self._next_value(argument, pos - 1)
                min_val = max(value_range.min, self.parse_value(min_value))
                max_val = min(value_range.max, self.parse_value(value))
                all_values.extend([i for i in range(min_val, max_val + 1)])

            elif symbol == '*':
                all_values.extend([i for i in range(value_range.min, value_range.max + 1)])
                break
            value, pos = self._next_value(argument, pos - 1)
        if value:
            all_values.append(self.parse_value(value))

        all_values = set(all_values)
        all_values = [value for value in all_values if value_range.min <= value <= value_range.max]
        all_values.sort()
        return all_values

    def _read_range(self, argument: str, pos: int,) -> Tuple[List[int], int]:
        value_range = copy(self._value_range)
        value_max, pos = self._next_value(argument, pos)
        if value_max:
            value_range.max = min(value_range.max, self.parse_value(value_max))

        symbol = argument[pos]
        if symbol == '-':
            value_min, pos = self._next_value(argument, pos - 1)
            value_range.min = max(value_range.min, self.parse_value(value_min))
        elif symbol == '*':
            pos -= 1

        return [i for i in range(value_range.min, value_range.max + 1)], pos

    @staticmethod
    def parse_number(value: str) -> int:
        if not value.isnumeric():
            raise CronException(f"Invalid argument: '{value}'")
        return int(value)

    @staticmethod
    def _next_value(command: str, pos: int) -> Tuple[str, int]:
        chars = []
        while pos >= 0 and command[pos] not in {'/', '*', '-', ','}:
            chars.append(command[pos])
            pos -= 1
        chars = chars[::-1]  # reverse the list
        value = "".join(chars)
        return value, pos

    @abstractmethod
    def parse_value(self, value: str) -> int:
        pass


class NumericParser(ArgumentParser):

    def parse_value(self, value: str) -> int:
        return self.parse_number(value)


class MonthParser(ArgumentParser):

    def __init__(self):
        super().__init__(Range(1, 12))
        self.__mapping: Dict[str, int] = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                                          "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}

    def parse_value(self, value: str) -> int:
        value = value.lower()
        if value in self.__mapping:
            return self.__mapping[value]
        return self.parse_number(value)


class WeekdayParser(ArgumentParser):

    def __init__(self):
        super().__init__(Range(1, 7))
        self.__mapping: Dict[str, int] = {"mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6, "sun": 7}

    def parse_value(self, value: str) -> int:
        value = value.lower()
        if value in self.__mapping:
            return self.__mapping[value]
        return self.parse_number(value)


def format_line(field_name: str, value: str) -> str:
    return f"{field_name:<14} {value}"


def parse(cron_str: str) -> List[str]:
    arguments = cron_str.split()
    if len(arguments) != 6:
        message = "Invalid number of arguments in a cron string.\n"\
                  "Required cron string arguments: \"minute hour day-of-month month day-of-week command\"\n\n"\
                  "Usage: python3 cron.py \"<cron-arguments>\""
        print(message)
        return [message]

    command = arguments[-1]
    arguments = arguments[:-1]
    field_names = ["minute", "hour", "day of month", "month", "day of week"]
    parsers = [NumericParser(Range(0, 59)),
               NumericParser(Range(0, 23)),
               NumericParser(Range(1, 31)),
               MonthParser(), WeekdayParser()]

    # We'll collect the lines that are printed in a list (convenient for unit-testing)
    printed_lines: List[str] = []
    for field_name, argument, parser in zip(field_names, arguments, parsers):
        try:
            values = parser.parse_argument(argument)
        except CronException as ex:
            print(str(ex))
            return [str(ex)]

        values = " ".join([str(value) for value in values])
        line = format_line(field_name, values)
        printed_lines.append(line)
        print(line)

    command_line = format_line("command", command)
    printed_lines.append(command_line)
    print(command_line)
    return printed_lines


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No cron string provided.\nUsage: python3 cron.py \"<cron-arguments>\"")
    else:
        cron_string = sys.argv[1]
        parse(cron_string)

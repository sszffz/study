"""
stock state. Like whether it is still active. It is saved as the an entry in the
database file. It keeps a dictionary and can be converted to a string so that it
can be save to database file. Or convert from string so that manager can query
the state.
The format is key1=value|key2=value
"""
from enum import Enum


class StateKey(Enum):
    """
    list of all possible key for state
    """
    ACTIVE = (0, "active", "bool", "is stock still active")
    LAST_UPDATE = (1, "last_update", "str", "last date to update successfully")
    ATTEMPTS = (2, "attempt", "int", "number of failure when attempt")

    def get_key(self):
        return self.value[1]

    def get_type(self):
        return self.value[2]


class StockState:

    __DELIMITER: str = "|"
    __SEPARATOR: str = "="
    __NA = "n/a"

    def __init__(self, state_str: str):
        self.__state_dict = dict()
        self.__parse(state_str)

    def __parse(self, state_str: str):
        """
        parse a string for all state
        :param state_str:
        :return:
        """
        if state_str is None or len(state_str) == 0:
            return

        state_str = state_str.strip()
        if state_str == self.__NA:
            return

        for item in state_str.split(self.__DELIMITER):
            self.__parse_item(item)

    def __parse_item(self, item: str):
        """
        parse a string for an item
        :param item:
        :return:
        """
        if item is None or len(item) == 0:
            return

        item = item.strip()
        key_value_pair = item.split(self.__SEPARATOR)
        if key_value_pair is None or len(key_value_pair) != 2:
            return

        key = key_value_pair[0].strip()
        value = key_value_pair[1].strip()

        if key is None or value is None:
            return

        for k in StateKey:
            if key == k.get_key():
                v = self.__parse_value(value, k.get_type())
                if v is not None:
                    self.__state_dict[k] = v
                break

    def __parse_value(self, value: str, data_type: str):
        """
        parse value
        :param value:
        :param data_type:
        :return:
        """
        if data_type == "bool":
            return self.__parse_bool_value(value)
        elif data_type == "int":
            return self.__parse_int_value(value)
        elif data_type == "float":
            return self.__parse_float_value(value)
        elif data_type == "str":
            return self.__parse_str_value(value)
        return None

    @staticmethod
    def __parse_bool_value(value: str) -> [bool, None]:
        """
        parse boolean value
        :param value:
        :return:
        """
        if not value:
            return None

        return value.lower() == "true"

    @staticmethod
    def __parse_int_value(value: str) -> [int, None]:
        """
        parse a int value
        :param value:
        :return:
        """
        if not value:
            return None

        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def __parse_float_value(value: str) -> [float, None]:
        """
        parse a float value
        :param value:
        :return:
        """
        if not value:
            return None

        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def __parse_str_value(value: str) -> [str, None]:
        """
        parse string
        """
        if value is None:
            return None

        return value

    @property
    def update_date(self) -> str:
        """
        get update date
        :return:
        """
        return self.__state_dict[StateKey.LAST_UPDATE] if StateKey.LAST_UPDATE in self.__state_dict else None

    @update_date.setter
    def update_date(self, update_date: str):
        if update_date:
            self.__state_dict[StateKey.LAST_UPDATE] = update_date

    @property
    def attempts(self) -> int:
        """
        Get the number of attempts of failure
        :return:
        """
        return self.__state_dict[StateKey.ATTEMPTS] if StateKey.ATTEMPTS in self.__state_dict else 0

    @attempts.setter
    def attempts(self, n: int):
        """
        Set the number attempts of failure
        :param n:
        :return:
        """
        self.__state_dict[StateKey.ATTEMPTS] = n

    def increase_attempts(self):
        """
        Increase attempts by 1
        :return:
        """
        # self.__state_dict[StateKey.ATTEMPTS] = self.attempts + 1
        self.attempts = self.attempts + 1

    def __str__(self):
        """
        convert to a string
        :return:
        """
        item_str_list = []
        for k in StateKey:
            if k in self.__state_dict:
                item_str_list.append("{}{}{}".format(k.get_key(), self.__SEPARATOR, str(self.__state_dict[k])))

        return self.__DELIMITER.join(item_str_list) if item_str_list else self.__NA

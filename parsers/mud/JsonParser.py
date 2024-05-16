#!/usr/bin/python3

import json
from parsers.mud.MudParser import MudParser


class JsonParser(MudParser):
    """
    JSON-format MUD file parser.
    """

    def read_input(self) -> dict:
        """
        Read the input MUD file as a dictionary.

        :return: dictionary containing data read from the input MUD file
        """
        data = None
        with open(self.input, "r") as json_file:
            data = json.load(json_file)
        return data

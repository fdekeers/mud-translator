#!/usr/bin/python3

import xml.etree.ElementTree as ET
from parsers.mud.MudParser import MudParser


class XmlParser(MudParser):
    """
    XML-format MUD file parser.
    """


    def element_to_dict(self, element: ET.Element) -> dict:
        """
        Recursively convert XML elements to a dict.

        :param element: XML tree element to start recursive parsing
        :return: dict containing the parsed XML elements
        """
        result = {}
        for child in element:
            if child:
                child_dict = self.element_to_dict(child)
                if child.tag in result:
                    if isinstance(result[child.tag], list):
                        result[child.tag].append(child_dict)
                    else:
                        result[child.tag] = [result[child.tag], child_dict]
                else:
                    result[child.tag] = child_dict
            else:
                result[child.tag] = child.text
        return result


    def read_input(self) -> dict:
        """
        Read the input MUD file as a dictionary.

        :return: dict containing data read from the input MUD file
        """
        tree = ET.parse(self.input)
        root = tree.getroot()
        return self.element_to_dict(root)

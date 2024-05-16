#!/usr/bin/python3

from enum import Enum

class Direction(Enum):
        """
        Enumerate the different types of traffic directions.
        """
        FROM = "from-device"
        TO   = "to-device"

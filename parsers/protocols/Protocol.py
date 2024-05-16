#!/usr/bin/python3

from __future__ import annotations
import importlib
from parsers.Direction import Direction


class Protocol:
    """
    Default Protocol parser.
    """

    # Mapping between supported MUD protocols
    # and corresponding protocol parsers
    protocols = {
        "ipv4": "Network",
        "ipv6": "Network",
        "tcp": "Transport",
        "udp": "Transport",
        "icmp": "icmp"
    }


    @classmethod
    def init_protocol(c, protocol_name: str) -> Protocol:
        """
        Initialize the protocol parser.

        :param protocol_name: name of the protocol
        :return: protocol parser object
        :raises ValueError: unsupported protocol
        """
        module_name = c.protocols.get(protocol_name, None)
        if module_name is not None:
            module = importlib.import_module(f"parsers.protocols.{module_name}")
            cls = getattr(module, module_name)
            return cls(protocol_name)
        else:
            raise ValueError(f"Unsupported protocol '{protocol_name}'")
    

    def __init__(self, protocol_name: str) -> None:
        """
        Constructor for the Protocol class.

        :param protocol_name: name of the protocol
        """
        self.name = protocol_name
    

    def parse(self, matches: dict, direction: Direction, is_local_network: bool, direction_initiated: Direction) -> dict:
        """
        Parse the protocol matches.

        :param matches: dict of protocol matches read from the MUD file
        :param direction: direction of the traffic (FROM or TO)
        :param is_local_network: whether the traffic is within the local network
        :param direction_initiated: direction of initiation of the connection (FROM or TO)
        :return: dict of protocol matches for the YAML profile
        :raises NotImplementedError: concrete protocol subclass must implement the parse method
        """
        raise NotImplementedError("Concrete protocol subclass must implement the parse method")

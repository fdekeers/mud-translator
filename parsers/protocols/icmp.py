#!/usr/bin/python3

from parsers.protocols.Protocol import Protocol
from parsers.Direction import Direction


class icmp(Protocol):
    """
    ICMP protocol parser.
    """

    # Supported fields
    fields = [
        "type",
        "code"
    ]

    # ICMP opcode to name mapping
    icmp_codes = {
        0: "echo-reply",
        3: "destination-unreachable",
        4: "source-quench",
        5: "redirect",
        8: "echo-request",
        11: "time-exceeded",
        12: "parameter-problem",
        13: "timestamp-request",
        14: "timestamp-reply",
        15: "information-request",
        16: "information-reply",
        17: "address-mask-request",
        18: "address-mask-reply"
    }
    

    def parse_type(self, opcode: int) -> str:
        """
        Parse the ICMP type match.

        :param opcode: ICMP type opcode match
        :return: string of ICMP type match for the YAML profile
        :raises ValueError: if the given ICMP opcode is invalid
        """
        icmp_type = self.icmp_codes.get(opcode, None)

        # Verify ICMP code
        if icmp_type is None:
            raise ValueError(f"Invalid ICMP opcode '{opcode}'")
        
        # ICMP code is valid
        return icmp_type


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
        # Initialize result dict
        proto_dict = {}

        # Parse fields
        for mud_field in self.fields:
            type_match = matches.get(mud_field, None)
            if type_match is not None:
                proto_dict["type"] = self.parse_type(type_match)

        return proto_dict

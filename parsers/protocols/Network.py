#!/usr/bin/python3

import re
import ipaddress
from parsers.Direction import Direction
from parsers.protocols.Protocol import Protocol


class Network(Protocol):
    """
    Network layer (IPv4 or v6) protocol parser.
    """

    # Mapping between supported MUD fields
    # and corresponding YAML profile fields
    fields = {
        "source-network": "src",
        "ietf-acldns:src-dnsname": "src",
        "destination-network": "dst",
        "ietf-acldns:dst-dnsname": "dst"
    }

    # Regex for domain name validation
    dns_regex = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\.\-]{1,253}[a-zA-Z0-9]$")


    def parse_network(self, mud_field: str, network_match: dict) -> str:
        """
        Parse a network match.

        :param mud_field: name of the MUD field
        :param network_match: dict of network match
        :return: string of network match for the YAML profile
        :raises ValueError: if the network match is invalid
        """
        # If field is domain name, check if it is valid
        if "ietf-acldns" in mud_field:
            if not self.dns_regex.match(network_match):
                raise ValueError(f"Invalid domain name '{network_match}'")
            # Domain name is valid
            return network_match
        
        # Field is IP network, check if it is valid
        try:
            ipaddress.ip_network(network_match)
        except ValueError:
            raise ValueError(f"Invalid network '{network_match}'")
        
        # Network is valid
        return str(network_match)


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
        for mud_field, yaml_field in self.fields.items():
            net_match = matches.get(mud_field, None)
            if net_match is not None:
                proto_dict[yaml_field] = self.parse_network(mud_field, net_match)
        
        # If local network, add corresponding address, depending on direction
        if is_local_network:
            if direction == Direction.FROM:
                proto_dict["dst"] = "local"
            elif direction == Direction.TO:
                proto_dict["src"] = "local"

        # If direction and direction initiated are different,
        # swap source and destination addresses
        if direction_initiated is not None and direction != direction_initiated:
            src = proto_dict.get("src", None)
            dst = proto_dict.get("dst", None)
            if src is not None:
                proto_dict["dst"] = src
                del proto_dict["src"]
            if dst is not None:
                proto_dict["src"] = dst
                del proto_dict["dst"]

        return proto_dict


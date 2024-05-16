#!/usr/bin/python3

from __future__ import annotations
import importlib
from argparse import Namespace
from enum import Enum
import yaml
from parsers.Direction import Direction
from parsers.protocols.Protocol import Protocol


class MudParser:
    """
    MUD file Parser.
    """

    # Global variables
    MUD  = "ietf-mud:mud"
    ACL  = "ietf-access-control-list:access-lists"
    FROM = "from-device-policy"
    TO   = "to-device-policy"
    DIRECTION_INIT = "ietf-mud:direction-initiated"
    supported_protocols = [
        "ipv4",
        "ipv6",
        "tcp",
        "udp",
        "icmp"
    ]

    class Format(Enum):
        """
        Enumerate the different types of MUD profiles.
        """
        JSON = 1
        XML  = 2


    @classmethod
    def init_parser(c, args: Namespace) -> MudParser:
        """
        Initialize the parser.

        :param args: command line arguments
        :return: parser object
        :raises ValueError: unrecognized MUD file format
        """
        parser = None
        if args.input.endswith(".json"):
            parser = "JsonParser"
            # Set output file if not specified
            if args.output is None:
                args.output = args.input.replace(".json", ".yaml")
        elif args.input.endswith(".xml"):
            parser = "XmlParser"
            # Set output file if not specified
            if args.output is None:
                args.output = args.input.replace(".xml", ".yaml")
        else:
            raise ValueError("Unrecognized MUD file format")
        
        module = importlib.import_module(f"parsers.mud.{parser}")
        cls = getattr(module, parser)
        return cls(args)
    

    def __init__(self, args: Namespace) -> None:
        """
        Constructor for the MudParser class.

        :param args: command line arguments
        """
        self.input = args.input
        self.output = args.output
        self.mac = args.mac
        self.ipv4 = args.ipv4
        self.ipv6 = args.ipv6
        self.network = args.network
    

    def read_input(self) -> dict:
        """
        Read the input MUD file as a dictionary.
        Should be implemented by concrete parser subclass.

        :return: dictionary containing data read from the input MUD file
        :raises NotImplementedError: concrete parser subclass must implement the read_input method
        """
        raise NotImplementedError("Concrete parser subclass must implement the read_input method")


    def write_output(self, yaml_data: dict) -> None:
        """
        Write the output YAML file.

        :param yaml_data: dictionary containing data to be written in the output YAML file
        """
        with open(self.output, "w") as yaml_file:
            yaml.dump(yaml_data, yaml_file, default_flow_style=False)


    def parse(self) -> None:
        """
        Parse the input MUD file,
        translate it to the YAML format,
        and write the output to the given output file.
        """

        # Read input MUD file into a dictionary
        data = self.read_input()
        mud_data = data[self.MUD]
        acl_data = data[self.ACL]

        # Initialize output dictionary
        yaml_data = {}

        # Metadata
        yaml_data["device-info"] = {}
        yaml_data["device-info"]["name"] = mud_data["systeminfo"]
        if self.mac is not None:
            yaml_data["device-info"]["mac"] = self.mac
        if self.ipv4 is not None:
            yaml_data["device-info"]["ipv4"] = self.ipv4
        if self.ipv6 is not None:
            yaml_data["device-info"]["ipv6"] = self.ipv6
        if self.network is not None:
            yaml_data["device-info"]["network"] = self.network

        ## Parse ACL names from MUD container
        acls = {}
        # From device
        from_device_acls = mud_data[self.FROM]["access-lists"]["access-list"]
        for i in range(len(from_device_acls)):
            acls[from_device_acls[i]["name"]] = Direction.FROM
        # To device
        to_device_acls = mud_data[self.TO]["access-lists"]["access-list"]
        for i in range(len(to_device_acls)):
            acls[to_device_acls[i]["name"]] = Direction.TO

        # Initialize YAML single policies field
        yaml_data["single-policies"] = {}

        # Parse ACLs from ACL container
        for acl in acl_data["acl"]:

            # ACLs not referenced in MUD container: skip
            if acl["name"] not in acls.keys():
                continue

            # ACLs referenced in MUD container:
            # Parse and add entries to YAML data
            for ace in acl["aces"]["ace"]:
                direction = acls[acl["name"]]
                matches = ace["matches"]
                policy = {"protocols": {}}  # Policy for the YAML profile, will be populated by parsing
                protocols = policy["protocols"]

                # Local network source or destination IP address
                is_local_network = bool(matches.get(self.MUD, {}).get("local-networks", None))

                # Direction initiated
                direction_initiated = matches.get("tcp", {}).get(self.DIRECTION_INIT, None)
                if direction_initiated is not None:
                    direction_initiated = Direction(direction_initiated)

                # Parse protocol if supported
                for protocol_name in self.supported_protocols:
                    if protocol_name in matches:
                        protocol = Protocol.init_protocol(protocol_name)
                        protocol_matches = protocol.parse(matches[protocol_name], direction, is_local_network, direction_initiated)
                        if protocol_matches:
                            protocols[protocol.name] = protocol_matches
                
                # Policy metadata
                if direction_initiated is not None:
                    policy["bidirectional"] = True
                    policy["stats"] = {"rate": 0}

                # Add policy to YAML data
                yaml_data["single-policies"][ace["name"]] = policy

        # Write output YAML file
        self.write_output(yaml_data)

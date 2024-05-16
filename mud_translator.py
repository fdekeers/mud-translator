#!/usr/bin/python3

"""
Translate a MUD profile (JSON/XML) into a YAML extended profile.
"""

# Libraries
import argparse
import re
import ipaddress
# Custom modules
from parsers.mud.MudParser import MudParser


def mac_address_type(mac_address: str) -> str:
    """
    Check if the given argument is a valid MAC address.

    :param mac_address: given MAC address
    :return: MAC address if valid
    :raises argparse.ArgumentTypeError: invalid MAC address
    """
    # Define a regular expression pattern for a MAC address
    mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    # Check if given argument matches the MAC pattern
    if not mac_pattern.match(mac_address):
        raise argparse.ArgumentTypeError(f"Invalid MAC address: {mac_address}")
    return mac_address


##### MAIN #####
if __name__ == "__main__":
    
    ## Parse command line arguments
    arg_parser = argparse.ArgumentParser(description="Translate a MUD profile (JSON/XML) into a YAML extended profile.")
    # Positional (mandatory) argument: Input file
    arg_parser.add_argument("input", type=str, help="Input MUD file (JSON or XML)")
    # Optional argument #1: Output file
    arg_parser.add_argument("-o", "--output", type=str, help="Output YAML file")
    # Optional argument #2: device MAC address
    arg_parser.add_argument("-m", "--mac", type=mac_address_type, help="Device MAC address")
    # Optional argument #3: device IPv4 address
    arg_parser.add_argument("-4", "--ipv4", type=ipaddress.ip_address, help="Device IPv4 address")
    # Optional argument #4: device IPv6 address
    arg_parser.add_argument("-6", "--ipv6", type=ipaddress.ip_address, help="Device IPv6 address")
    # Optional argument #5: network interface
    arg_parser.add_argument("-n", "--network", type=str, choices=["wired", "wireless"], help="Network interface")
    # Parse arguments
    args = arg_parser.parse_args()

    # Parse input file
    mud_parser = MudParser.init_parser(args)
    mud_parser.parse()

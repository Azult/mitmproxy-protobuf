from mitmproxy import http
import mitmproxy
from sys import stdin, argv
from os.path import ismount, exists, join
from os import mkdir
from runpy import run_path
from lib.types import StandardParser
import uuid

def parse_proto(file):
    root_type = "root"
    # Load the config
    config = {}
    directory = "."
    while not ismount(directory):
        filename = join(directory, "protobuf_config.py")
        if exists(filename):
            config = run_path(filename)
            break
        directory = join(directory, "..")

    # Create and initialize parser with config
    parser = StandardParser()
    if "types" in config:
        for type, value in config["types"].items():
            assert(type not in parser.types)
            parser.types[type] = value
    if "native_types" in config:
        for type, value in config["native_types"].items():
            parser.native_types[type] = value

    # Make sure root type is defined and not compactable
    if root_type not in parser.types: parser.types[root_type] = {}
    parser.types[root_type]["compact"] = False

    # PARSE!
    return parser.safe_call(parser.match_handler("message"), file, root_type) + "\n"
    # exit(1 if len(parser.errors_produced) else 0)

file_path = 'tmp'

def response(flow: http.HTTPFlow):
    if "nova" in flow.request.pretty_url:
        
        #Parse request
        
        with open(file_path,"wb") as f:
            f.write(flow.request.content)
        with open(file_path,"rb") as f:
            # data = parse_proto(f)
            flow.request.raw_content = parse_proto(f).encode()

        #Parse response
        with open(file_path,"wb") as f:
            f.write(flow.response.raw_content)
        with open(file_path,"rb") as f:
            # data = parse_proto(f)
            flow.response.raw_content = parse_proto(f).encode()


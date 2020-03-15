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

dir_name = "out/" + str(uuid.uuid4())
mkdir(dir_name)
mkdir(dir_name + "/requests")
mkdir(dir_name + "/responses")
counter = 0

def response(flow: http.HTTPFlow):
    if "nova" in flow.request.pretty_url:
        global counter
        counter += 1
        data = ""
        
        #Parse request
        file_path = dir_name + "/requests/" + str(counter) + "_" + (flow.request.pretty_url).split("/")[-1]
        with open(file_path,"wb") as f:
            f.write(flow.request.content)
        with open(file_path,"rb") as f:
            data = parse_proto(f)
        with open(file_path,"w+") as f:
            f.write(data)

        #Parse response
        file_path = dir_name + "/responses/" + str(counter) + "_" + (flow.request.pretty_url).split("/")[-1]
        with open(file_path,"wb") as f:
            f.write(flow.response.raw_content)
        with open(file_path,"rb") as f:
            data = parse_proto(f)
        with open(file_path,"w+") as f:
            f.write(data)


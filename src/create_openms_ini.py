""" This module converts a JSON or YAML file into OpenMS INI file. For more
detail of OpenMS INI file format, see here:
https://abibuilder.informatik.uni-tuebingen.de/archive/openms/Documentation/
nightly/html/TOPP_general.html """
import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.dom import minidom


def parse_args() -> argparse.Namespace:
    """ parse args """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'INPUT',
        type=Path,
        help='Input file path'
    )
    parser.add_argument(
        'OUTPUT',
        type=Path,
        help='Output file path'
    )
    parser.add_argument(
        '--input-format',
        type=str,
        choices=['JSON', 'YAML'],
        default='JSON',
        help='Input file format. Defaults to JSON.'
    )
    return parser.parse_args()

def encode_bool_to_str(val:bool):
    """ Encode the bool variables from python style to OpenMS's style (C++
    style) """
    return 'true' if val else 'false'

def get_item_type(obj) -> str:
    """ Get item type in OpenMS style """
    mapper = {
        'str': 'string',
        'int': 'int',
        'float': 'double',
        'bool': 'bool'
    }
    item_type = obj.__class__.__name__
    if item_type not in mapper:
        raise ValueError('Value type not sopported')
    return mapper[item_type]

def add_subtree(element:ET.Element, data:dict):
    """ Add a subtree to a given element """
    for key,val in data.items():
        if isinstance(val, list):
            item_types = {get_item_type(v) for v in val}
            if len(item_types) > 1:
                raise ValueError('ITEMLIST should have the same type')
            item_type = item_types.pop()
            if item_type == 'bool':
                val = [encode_bool_to_str(v) for v in val]
            attrib = {
                'name': key,
                'type': item_type,
                'description': ''
            }
            itemlist = ET.SubElement(element, 'ITEMLIST', attrib=attrib)
            for _val in val:
                ET.SubElement(itemlist, 'LISTITEM', value=str(_val))
        elif isinstance(val, dict):
            subtree = ET.SubElement(element, 'NODE', name=key)
            add_subtree(subtree, val)
        else:
            item_type = get_item_type(val)
            if item_type == 'bool':
                val = encode_bool_to_str(val)
            attrib = {
                'name': key,
                'value': str(val),
                'type': item_type
            }
            ET.SubElement(element, 'ITEM', attrib=attrib)

def create_openms_ini(data:dict) -> ET.Element:
    """ Create OpenMS INI XML tree """
    root = ET.Element("PARAMETERS", version="1.1")
    for section_key, section_vals in data.items():
        section = ET.SubElement(root, 'NODE', name=section_key)
        section_vals:dict
        for program_name, program_args in section_vals.items():
            program = ET.SubElement(section, 'NODE', name=program_name)
            add_subtree(program, program_args)
    return root

def main():
    """ main """
    args = parse_args()
    with open(args.INPUT, 'rt') as handle:
        data = json.load(handle)
    ini = create_openms_ini(data)
    dom:minidom.Document = minidom.parseString(ET.tostring(ini, encoding='ISO-8859-1'))
    dom = dom.toprettyxml(indent = '  ')
    with open(args.OUTPUT, 'w') as handle:
        handle.write(dom)

if __name__ == '__main__':
    main()

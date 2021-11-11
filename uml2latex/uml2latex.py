# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

import xml.etree.ElementTree as ET
import argparse
import os
import sys
import glob
import tempfile

from uml2latex.utils import *
from uml2latex.parse import UMLData
from uml2latex.data import *
from uml2latex.diagrams import make_single_class_diagram
from uml2latex.override import Override

file_header = """% Diese Datei wurde automatisch generiert.
% Sie zu bearbeiten, ist dementsprechend sinnlos.
% Nutzen Sie stattdessen die Dateien in template_override, um die Darstellung anzupassen.\n"""

default_root_template = [
    ("%MODULES", make_module_list),
    ("%DIAGRAMS", make_manual_diagrams),
    ("%DESCRIPTIONS", make_class_descriptions),
    ("%SEQUENCES", make_sequence_diagrams),
]

default_templates = {
    "modules" : [
        ("%HEADER", make_module_header),
        ("%DESCRIPTION", make_module_description),
        ("%CLASSLIST", make_module_classlist),
        ("%DIAGRAM", make_module_diagram),
    ],
    "manual_diagrams" : [
        ("%HEADER", make_diagram_header),
        ("%DESCRIPTION", make_diagram_description),
        ("%DIAGRAM", make_diagram_diagram),
    ],
    "manual_diagrams_no_desc" : [
        ("%DIAGRAM", make_diagram_diagram_with_section),
    ],
    "class_descriptions" : [
        ("%HEADER", make_class_header),
        ("%DIAGRAM", make_class_single_diagram),
        ("%DESCRIPTION", make_class_description),
        ("%TEMPLATE", make_class_template_list),
        ("%OPERATIONS", make_class_operations_list),
        ("%ATTRIBUTES", make_class_attributes_list),
        ("%CHILDREN", make_class_child_list),
        ("%DEPENDENCIES", make_class_dependency_list),
        ("%ASSOCIATIONS", make_class_association_list),
    ],
}

def read_args():
    parser = argparse.ArgumentParser(description="Create LaTeX documentation from an Umbrello file")
    parser.add_argument("file", metavar="FILE", help="The Umbrello UML file to read")
    parser.add_argument("-n", "--no-pics", default=False, action="store_true", help="Do not generate class diagram images")
    parser.add_argument("-o", "--output", default=None, help="Output to the given file instead of stdout")
    parser.add_argument("-t", "--templates", default="template_override", help="The directory to read template override files from ('template_override' by default)")
    parser.add_argument("-i", "--outImages", default="outImages", help="The directory to place the produced images in ('outImages' by default)")
    return parser.parse_args()

def get_output(file):
    if file is None:
        return sys.stdout
    else:
        return open(file, "w")

def main():
    args = read_args()

    umlData = UMLData.parse_uml(args.file)

    override = Override(args.templates)

    # Make a new extension element for the single diagrams
    ext = ET.SubElement(umlData.tree.getroot()[1][0][0][4], "XMI.extension", {"xmi.extender": "umbrello"})
    single_diagram_list = ET.SubElement(ext, "diagrams")

    for cl in {i:el for (i, el) in umlData.elements.items() if el.ty == ElementType.CLASS}.values():
        make_single_class_diagram(single_diagram_list, cl, override.custom_width)

    if not args.no_pics:
        # Let Umbrello generate the images for us
        tmpfile, tmppath = tempfile.mkstemp(prefix="uml")
        umlData.tree.write(tmpfile, xml_declaration=True, encoding="utf-8")
        try:
            os.mkdir(args.outImages)
        except:
            pass
        os.system("umbrello5 --directory {} --export svg {}".format(args.outImages, tmppath))

        for file in glob.glob("{}/*.svg".format(args.outImages)):
            print(file)
            os.system("rsvg-convert \"" + file + "\" -f pdf > \"" + space_ul(file[:file.find("svg", -1) - 2]) + "pdf\"")
            os.remove(file)
        os.remove(tmppath);

    sorted_manual_diagram_list = sort_by_order(umlData.class_diagram_list,
            override.diagram_order, lambda x, name: x.attrib["name"] == name)

    sorted_sequence_diagram_list = sort_by_order(umlData.sequence_diagram_list,
            override.sequence_diagram_order, lambda x, name: x.attrib["name"] == name)

    sorted_package_list = list(umlData.packages.items())
    sorted_package_list = sort_by_order(list(umlData.packages.items()),
            override.module_list_order, lambda x, name: x[0].attrib["name"] == name)

    for i, (package, classes) in enumerate(sorted_package_list):
        if package.attrib["name"] in override.module_order:
            sorted_package_list[i] = (package, sort_by_order(classes,
                override.module_order[package.attrib["name"]], lambda x, name: x.name == name))

    # Generate templates for LaTeX
    with get_output(args.output) as f:
        f.write(file_header)
        f.write(format_template(default_root_template, override.root,
            default_templates, sorted_package_list, sorted_manual_diagram_list, sorted_sequence_diagram_list,
            umlData.elements, override, override.noref))

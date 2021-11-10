# coding=utf-8
import xml.etree.ElementTree as ET
import shutil
import os
import sys
import glob
from functions import *

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

override = {}
for file in glob.glob("./template_override/*"):
    with open(file, "r") as f:
        override[file.split("/")[-1]] = f.read()

shutil.copy("UML.xmi", "tmp_file.xmi")
ET.register_namespace("UML", umlSchema[1:-1])
tree = ET.parse("tmp_file.xmi")

model_view = tree.getroot()[1][0][0][3]
namespace_root = model_view.find(umlSchema + "Namespace.ownedElement")

package_list = list(filter(lambda x: "stereotype" not in x.attrib or x.attrib["name"] != "Datatypes",
    namespace_root.findall(umlSchema + "Package")))
package_list.append(model_view)

manual_diagram_list_root = model_view.find("XMI.extension")
manual_diagram_list = list(manual_diagram_list_root[0].findall("diagram"))

sequence_diagram_list_root = next(filter(lambda x: x.attrib["name"] == "Sequenzdiagramme",
    namespace_root.findall(umlSchema + "Package"))).find("XMI.extension")
sequence_diagram_list = list(sequence_diagram_list_root[0].findall("diagram"))

# Make a new extension element for the single diagrams
ext = ET.SubElement(tree.getroot()[1][0][0][4], "XMI.extension", {"xmi.extender": "umbrello"})
single_diagram_list = ET.SubElement(ext, "diagrams")

custom_width_lines = []
if "CUSTOM_WIDTH" in override:
    custom_width_lines = override["CUSTOM_WIDTH"].split("\n")
custom_width = dict([tuple(s.split(" ")) for s in custom_width_lines[:-1]])

# Contains ALL elements (including DataTypes) by xmi.id
elements = {}
# Contains only classes / interfaces / enums by package
packages = {}
for package in package_list:
    package_namespace = package.find(umlSchema + "Namespace.ownedElement")
    class_list = package_namespace.findall(umlSchema + "Class")
    class_list.extend(package_namespace.findall(umlSchema + "Interface"))
    class_list.extend(package_namespace.findall(umlSchema + "Enumeration"))
    class_dict = parse_classes(single_diagram_list, class_list, package.attrib["name"], custom_width)
    elements.update(class_dict)
    packages[package] = list(filter(lambda x: x.ty in ["Class", "Interface", "Enumeration"],
        class_dict.values()))

for datatype in namespace_root[0][0].findall(umlSchema + "DataType"):
    elements[datatype.attrib["xmi.id"]] = DataType(
            escape(datatype.attrib["name"]),
            datatype.attrib["xmi.id"],
            datatype.attrib["comment"] if "comment" in datatype.attrib else None)

# Abstraction ~= Inheritance in UML-speak
for abstraction in namespace_root.findall(umlSchema + "Abstraction"):
    elements[abstraction.attrib["client"]].abstraction = abstraction.attrib["supplier"]
    elements[abstraction.attrib["supplier"]].children.append(abstraction.attrib["client"])

for generalization in namespace_root.findall(umlSchema + "Generalization"):
    elements[generalization.attrib["child"]].abstraction = generalization.attrib["parent"]
    elements[generalization.attrib["parent"]].children.append(generalization.attrib["child"])

for dependency in namespace_root.findall(umlSchema + "Dependency"):
    if dependency.attrib["client"] not in elements or dependency.attrib["supplier"] not in elements:
        continue
    elements[dependency.attrib["client"]].dependencies.append(Dependency(
    dependency.attrib["supplier"], dependency.attrib["comment"] if "comment" in dependency.attrib else None))

for association in namespace_root.findall(umlSchema + "Association"):
    for start in association[0]:
        for end in association[0]:
            client = start.attrib["type"]
            target = end.attrib["type"]
            if start == end or client not in elements or target not in elements \
                    or next(filter(lambda x: x.target == target, elements[end.attrib["type"]].associations), None) is not None \
                    or end.attrib["isNavigable"] == "false":
                continue
            
            elements[client].associations.append(Association(
                end.attrib["name"] if len(end.attrib["name"]) > 0 else association.attrib["name"],
                end.attrib["type"],
                end.attrib["multiplicity"] if "multiplicity" in end.attrib else None,
                end.attrib["comment"] if "comment" in end.attrib else None))

make_pics = True
if len(sys.argv) >= 2 and sys.argv[1] == "--no-pics":
    make_pics = False
if make_pics:
    # Let Umbrello generate the images for us
    tree.write("tmp_file.xmi", xml_declaration=True, encoding="utf-8")
    try:
        os.mkdir("outImages")
    except:
        pass
    os.system("umbrello5 --directory outImages --export svg tmp_file.xmi")

    for file in glob.glob("./outImages/*.svg"):
        print(file)
        os.system("rsvg-convert \"" + file + "\" -f pdf > \"" + space_ul(file[:file.find("svg", -1) - 2]) + "pdf\"")
        os.remove(file)
os.remove("tmp_file.xmi")

no_ref = []
if "NOREF" in override:
    no_ref = override["NOREF"].split("\n")

sorted_manual_diagram_list = manual_diagram_list
if "DIAGRAM_ORDER" in override:
    sorted_manual_diagram_list = sort_by_order(manual_diagram_list,
            override["DIAGRAM_ORDER"], lambda x, name: x.attrib["name"] == name)

sorted_sequence_diagram_list = sequence_diagram_list
if "SEQUENCE_DIAGRAM_ORDER" in override:
    sorted_sequence_diagram_list = sort_by_order(sequence_diagram_list,
            override["SEQUENCE_DIAGRAM_ORDER"], lambda x, name: x.attrib["name"] == name)

sorted_package_list = list(packages.items())
if "MODULE_ORDER" in override:
    sorted_package_list = sort_by_order(list(packages.items()),
        override["MODULE_ORDER"], lambda x, name: x[0].attrib["name"] == name)

for i, (package, classes) in enumerate(sorted_package_list):
    order_name = package.attrib["name"] + "_order"
    if order_name in override:
        sorted_package_list[i] = (package, sort_by_order(classes,
            override[order_name], lambda x, name: x.name == name))

# Generate templates for LaTeX
with open("templates.tex", "w") as f:
    f.write(file_header)
    f.write(format_template(default_root_template, override, "ROOT",
        default_templates, sorted_package_list, sorted_manual_diagram_list, sorted_sequence_diagram_list,
        elements, override, no_ref))

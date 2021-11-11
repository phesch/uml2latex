# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

from uml2latex.tex.common import format_template
from uml2latex.tex.classes import make_class_descriptions
from uml2latex.tex.modules import make_module_list
from uml2latex.tex.diagrams import make_class_diagrams, make_sequence_diagrams

class TexInfo:
    file_header = """% Diese Datei wurde automatisch generiert.
% Sie zu bearbeiten, ist dementsprechend sinnlos.
% Nutzen Sie stattdessen die Dateien in template_override, um die Darstellung anzupassen.\n"""

    default_root_template = [
        ("%MODULES", make_module_list),
        ("%DIAGRAMS", make_class_diagrams),
        ("%DESCRIPTIONS", make_class_descriptions),
        ("%SEQUENCES", make_sequence_diagrams),
    ]

    def __init__(self, override, packages, class_diagrams, sequence_diagrams, elements, image_dir):
        self.override = override
        self.packages = packages
        self.class_diagrams = class_diagrams
        self.sequence_diagrams = sequence_diagrams
        self.elements = elements
        self.image_dir = image_dir

def generate_latex(umlData, image_dir, override):
    sorted_class_diagram_list = sort_by_order(umlData.class_diagram_list,
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
    info = TexInfo(override, sorted_package_list, sorted_class_diagram_list,
            sorted_sequence_diagram_list, umlData.elements, image_dir)

    return TexInfo.file_header + format_template(TexInfo.default_root_template, override.root, info)

def sort_by_order(collection, order, func):
    if not order:
        return collection
    sorted_list = []
    for name in order:
        nxt = next((x for x in collection if func(x, name)), None)
        if nxt is not None:
            sorted_list.append(nxt)
    return sorted_list


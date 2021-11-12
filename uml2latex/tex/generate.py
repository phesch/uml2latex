# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2021 phesch <phesch@phesch.de>

# This file is part of uml2latex.
#
# uml2latex is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# uml2latex is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with uml2latex.  If not, see <https://www.gnu.org/licenses/>.

"""Main file for LaTeX template generation."""

from uml2latex.tex.common import format_template
from uml2latex.tex.classes import make_class_descriptions
from uml2latex.tex.modules import make_module_list
from uml2latex.tex.diagrams import make_class_diagrams, make_sequence_diagrams

class TexInfo:
    """Holds information required to format a LaTeX file from UML data.

    Attributes:
        file_header: (static) A header to prepend to the generated text.
        default_root_template: (static) The template macro parameters and functions
            used for LaTeX document generation.
        override: Override information for customizing document generation.
        packages: A dict of package names and their member classes to generate LaTeX for.
        class_diagrams: A list of class diagrams to generate LaTeX for.
        sequence_diagrams: A list of sequence diagrams to generate LaTeX for.
        elements: A dict of UML elements used for references.
        image_dir: The directory that diagrams can be found in.
    """
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
    """Generate LaTeX from the given UMLData and custom overrides.

    Args:
        umlData: The UMLData to generate LaTeX formatting for.
        image_dir: The directory that diagrams can be found in.
        override: Override information for customizing document generation.
    """
    sorted_class_diagram_list = _sort_by_order(umlData.class_diagram_list,
            override.diagram_order, lambda x, name: x.attrib["name"] == name)

    sorted_sequence_diagram_list = _sort_by_order(umlData.sequence_diagram_list,
            override.sequence_diagram_order, lambda x, name: x.attrib["name"] == name)

    sorted_package_list = list(umlData.packages.items())
    sorted_package_list = _sort_by_order(list(umlData.packages.items()),
            override.module_list_order, lambda x, name: x[0].attrib["name"] == name)

    for i, (package, classes) in enumerate(sorted_package_list):
        if package.attrib["name"] in override.module_order:
            sorted_package_list[i] = (package, _sort_by_order(classes,
                override.module_order[package.attrib["name"]], lambda x, name: x.name == name))
    info = TexInfo(override, sorted_package_list, sorted_class_diagram_list,
            sorted_sequence_diagram_list, umlData.elements, image_dir)

    return TexInfo.file_header + format_template(TexInfo.default_root_template, override.root, info)

def _sort_by_order(collection, order, func):
    if not order:
        return collection
    sorted_list = []
    for name in order:
        nxt = next((x for x in collection if func(x, name)), None)
        if nxt is not None:
            sorted_list.append(nxt)
    return sorted_list


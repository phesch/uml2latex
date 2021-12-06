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

"""Generates LaTeX formatting for module listings."""

from uml2latex.tex.common import *
from uml2latex.tex.diagrams import DiagramInfo, make_diagram_image

def _make_module_header(modinfo):
    return "\t\\subsection{{{0}}}\n".format(modinfo.module.attrib["name"])

def _make_module_description(modinfo):
    return "\t\t{0}\n".format(attrdoc(modinfo.module.attrib, "comment", modinfo.module.attrib["name"]))

def _make_module_classlist(modinfo):
    if not modinfo.classes:
        return ""
    text = "\t\t\\subsubsection*{Klassen}\n"
    text += beginMultiColItem
    for cl in modinfo.classes:
        text += "\t\t\t\t\t\t\\item \\nameref{{{0}}}\n".format(cl.name)
    text += endMultiColItem
    return text

def _make_module_diagram(modinfo):
    diagram = next((d for d in modinfo.diagrams \
            if d.attrib["name"].casefold() == modinfo.module.attrib["name"].casefold()), None)
    if diagram is not None:
        modinfo.diagrams.remove(diagram)
        return make_diagram_image(DiagramInfo(diagram, modinfo.image_dir))
    return ""

class ModuleInfo:
    """Holds information required to format a module listing in LaTeX.

    Attributes:
        module_template: (static) The template macro parameters and functions
            used for a module listing.
        module: The module to format the listing for.
        classes: A list of member classes of the module.
        diagrams: A class diagram that shows the module.
        image_dir: The directory the diagram can be found in.
    """

    module_template = [
        ("%HEADER", _make_module_header),
        ("%DESCRIPTION", _make_module_description),
        ("%CLASSLIST", _make_module_classlist),
        ("%DIAGRAM", _make_module_diagram),
    ]

    def __init__(self, module, classes, diagrams, image_dir):
        self.module = module
        self.classes = classes
        self.diagrams = diagrams
        self.image_dir = image_dir

def make_module_list(tex_info):
    text = "\t\\section{Architektur}\n"
    text += tex_info.override.architecture_desc
    for package, classes in tex_info.packages:
        text += format_template(ModuleInfo.module_template,
                get(tex_info.override.module_listing, package.attrib["name"]),
                ModuleInfo(package, classes, tex_info.class_diagrams, tex_info.image_dir))
    return text

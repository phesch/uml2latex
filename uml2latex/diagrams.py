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

"""Code for generating diagrams containing only a single class."""

import xml.etree.ElementTree as ET

from uml2latex.data import *

# Template for diagram XML element
diagramTemplate = {
        "usefillcolor": "1",
        "showpackage": "1",
        "type": "1",
        "linewidth": "0",
        "textcolor": "#000000",
        "snapcsgrid": "0",
        "name": "Diagram_",
        "documentation": "",
        "canvaswidth": "500",
        "linecolor": "#ff0000",
        "snapx": "25",
        "snapy": "25",
        "canvasheight": "500",
        "snapgrid": "0",
        "showatts": "1",
        "showscope": "1",
        "showstereotype": "1",
        "showopsig": "1",
        "isopen": "1",
        "fillcolor": "#ffffc0",
        "showops": "1",
        "backgroundcolor": "#ffffff",
        "showpubliconly": "0",
        "zoom": "100",
        "showattribassocs": "1",
        "showattsig": "1",
        "griddotcolor": "#f7f7f7",
        "font": "Noto Sans Mono,9,-1,5,50,0,0,0,0,0,Regular",
        "localid": "-1",
        "xmi.id": "diag_",
        "showgrid": "0"
        }

# Template for class / interface / enum XML element
classTemplate = {
        "usefillcolor": "1",
        "usesdiagramfillcolor": "0",
        "showoperations": "1",
        "showpackage": "1",
        "usesdiagramusefillcolor": "0",
        "linewidth": "1",
        "showopsigs": "601",
        "textcolor": "#000000",
        "x": "-178",
        "y": "-178",
        "height": -1,
        "linecolor": "#ff0000",
        "autoresize": "1",
        "width": "700",
        "showscope": "1",
        "showstereotype": "1",
        "fillcolor": "#ffffc0",
        "showattributes": "",
        "showpubliconly": "0",
        "font": "Noto Sans Mono,9,-1,5,50,0,0,0,0,0,Regular",
        "isinstance": "0",
        "localid": "uHVRIOTyOW7Yf",
        "showattsigs": "601",
        "xmi.id": ""
        }

def make_single_class_diagram(parent, cl, custom_widths):
    """Place a single class diagram in an XML tree.

    Args:
        parent: The XML element to create the diagram under.
        cl: The class to create the diagram for.
        custom_widths: A dictionary of custom width assignments.
            If cl is contained in this dict, the custom width is applied.
    """
    diagAttrs = dict(diagramTemplate)
    diagAttrs["name"] += cl.name
    diagAttrs["xmi.id"] += cl.name
    diagram = ET.SubElement(parent, "diagram", dict(diagAttrs))
    widgets = ET.SubElement(diagram, "widgets")

    # Umbrello complains if we don't set the tag correctly
    tags = {ClassType.CLASS: "classwidget", ClassType.INTERFACE: "interfacewidget", ClassType.ENUM: "enumwidget"}
    tag = tags[cl.class_type]

    classAttrs = dict(classTemplate)
    classAttrs["height"] = str(cl.approx_height)
    if cl.name in custom_widths:
        classAttrs["width"] = custom_widths[cl.name]
    classAttrs["showattributes"] = "1" if cl.class_type == ClassType.CLASS else "0"
    classAttrs["xmi.id"] = cl.xmiId
    classwidget = ET.SubElement(widgets, tag, classAttrs)

    # These also seem to be necessary
    messages = ET.SubElement(diagram, "messages")
    associations = ET.SubElement(diagram, "associations")

def make_all_single_class_diagrams(tree, elements, custom_widths):
    """Create single class diagrams for every class in the elements given.

    Args:
        tree: The Umbrello XML tree to place the diagrams in.
        elements: The dictionary of elements to retrieve the classes from.
        custom_widths: A dictionary of custom width assignments.
            If a class name is a key, the value is used as its diagram's width.
    """
    ext = ET.SubElement(tree.getroot()[1][0][0][4], "XMI.extension", {"xmi.extender": "umbrello"})
    single_diagram_list = ET.SubElement(ext, "diagrams")

    for cl in [el for el in elements.values() if el.ty == ElementType.CLASS]:
        make_single_class_diagram(single_diagram_list, cl, custom_widths)

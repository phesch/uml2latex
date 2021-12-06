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

"""Code for parsing information from the Umbrello XML format."""

import xml.etree.ElementTree as ET

from uml2latex.data import *
from uml2latex.utils import escape

_umlSchema = "{http://schema.omg.org/spec/UML/1.4}"

class UMLData:
    """Parses and holds UML data read from XML.

    Do not instantiate this class directly, use the parse_uml function instead.
    It will return an instance of this class.

    Attributes:
        tree: The ElementTree read in by etree.
        packages: A dict of packages and their contents.
        elements: A dict of element names and their definitions.
        class_diagram_list: A list of class diagrams found in the XML.
        sequence_diagram_list: A list of sequence diagrams found in the XML.

    """

    tree = None
    packages = {}
    elements = {}
    class_diagram_list = []
    sequence_diagram_list = []

    def __init__(self, tree, packages, elements, class_diagram_list, sequence_diagram_list):
        self.tree = tree
        self.packages = packages
        self.elements = elements
        self.class_diagram_list = class_diagram_list
        self.sequence_diagram_list = sequence_diagram_list

    def _get_properties(cl, element_dict):
        """Get all the operations, attributes, and the template parameter of a class.

        Returns a tuple of a list of operations, a list of attributes,
        and a template parameter (or None if the class does not have one).

        Args:
            cl: The class of which to get the properties.
            element_dict: The dict to add the potential template parameter to.
        """
        operations = []
        attributes = []
        classifier = cl.find(_umlSchema + "Classifier.feature")
        if classifier is not None:
            operations = classifier.findall(_umlSchema + "Operation")
            attributes = classifier.findall(_umlSchema + "Attribute")
        model_element = cl.find(_umlSchema + "ModelElement.templateParameter")
        if model_element is not None:
            att = model_element[0].attrib
            element_dict[att["xmi.id"]] = Template(escape(att["name"]),
                    att["xmi.id"],
                    att["type"] if "type" in att else None,
                    att["comment"] if "comment" in att else None)
            return (operations, attributes, att["xmi.id"])
        return (operations, attributes, None)

    def _approximate_class_height(cl):
        """Roughly approximate how many vertical pixels are needed to render a diagram of the given class.

        This is necessary because we need to tell Umbrello how large to render each diagram -
        it doesn't infer that from the elements of the diagram.

        Args:
            cl: The class to approximate the height of.
        """
        height = 60
        classifier = cl.find(_umlSchema + "Classifier.feature")
        if classifier is not None:
            for el in classifier:
                height += 15
        return height


    def _parse_classes(class_list, package):
        """Parse all the classes in the list into Class objects and return them in a dict.

        Args:
            class_list: The list of classes to parse.
            package: Which package to assign the parsed classes to.
        """
        element_dict = {}
        for cl in class_list:
            (operations, attributes, template) = UMLData._get_properties(cl, element_dict)
            class_type = ClassType.CLASS if "Class" in cl.tag else (ClassType.INTERFACE if "Interface" in cl.tag else ClassType.ENUM)
            element_dict[cl.attrib["xmi.id"]] = Class(
                class_type,
                escape(cl.attrib["name"]),
                package,
                cl.attrib["xmi.id"],
                operations,
                attributes,
                None,
                template,
                cl.attrib["comment"] if "comment" in cl.attrib else None,
                UMLData._approximate_class_height(cl))
        return element_dict


    def parse_uml(file):
        """Parse an Umbrello XML tree into the UMLData format.

        This is kind of janky, so if something breaks after an Umbrello update involving an XML format change,
        check here first.
        This method expects your Umbrello project to have a particular structure (no nested packages or classes,
        all sequence diagrams in a folder called "Sequenzdiagramme").
        TODO: Make this method handle other project structures and nested packages gracefully.

        Args:
            file: The file to read the XML from.
        """
        ET.register_namespace("UML", _umlSchema[1:-1])
        tree = ET.parse(file)

        model_view = [el for el in tree.getroot()
            .find("./XMI.content/{0}Model/{0}Namespace.ownedElement".format(_umlSchema))
            .findall(_umlSchema + "Model") if el.attrib["xmi.id"] == "Logical_View"][0]
        namespace_root = model_view.find(_umlSchema + "Namespace.ownedElement")

        package_list = list(filter(lambda x: "stereotype" not in x.attrib or x.attrib["name"] != "Datatypes",
            namespace_root.findall(_umlSchema + "Package")))
        package_list.append(model_view)

        class_diagram_list_root = model_view.find("XMI.extension")
        class_diagram_list = list(class_diagram_list_root[0].findall("diagram"))

        sequence_diagram_list_root = next(filter(lambda x: x.attrib["name"] == "Sequenzdiagramme",
            namespace_root.findall(_umlSchema + "Package"))).find("XMI.extension")
        sequence_diagram_list = list(sequence_diagram_list_root[0].findall("diagram"))

        # Contains ALL elements (including DataTypes) by xmi.id
        elements = {}
        # Contains a list of classes / interfaces / enums by package
        packages = {}
        for package in package_list:
            package_namespace = package.find(_umlSchema + "Namespace.ownedElement")
            class_list = package_namespace.findall(_umlSchema + "Class")
            class_list.extend(package_namespace.findall(_umlSchema + "Interface"))
            class_list.extend(package_namespace.findall(_umlSchema + "Enumeration"))
            class_dict = UMLData._parse_classes(class_list, package.attrib["name"])
            elements.update(class_dict)
            packages[package] = list(filter(lambda x: x.ty == ElementType.CLASS,
                class_dict.values()))

        for datatype in namespace_root.find("./{0}Package/{0}Namespace.ownedElement".format(_umlSchema))\
                .findall(_umlSchema + "DataType"):
            elements[datatype.attrib["xmi.id"]] = DataType(
                    escape(datatype.attrib["name"]),
                    datatype.attrib["xmi.id"],
                    datatype.attrib["comment"] if "comment" in datatype.attrib else None)

        # Abstraction ~= Inheritance in UML-speak
        for abstraction in namespace_root.findall(_umlSchema + "Abstraction"):
            elements[abstraction.attrib["client"]].abstraction = abstraction.attrib["supplier"]
            elements[abstraction.attrib["supplier"]].children.append(abstraction.attrib["client"])

        for generalization in namespace_root.findall(_umlSchema + "Generalization"):
            elements[generalization.attrib["child"]].abstraction = generalization.attrib["parent"]
            elements[generalization.attrib["parent"]].children.append(generalization.attrib["child"])

        for dependency in namespace_root.findall(_umlSchema + "Dependency"):
            if dependency.attrib["client"] not in elements or dependency.attrib["supplier"] not in elements:
                continue
            elements[dependency.attrib["client"]].dependencies.append(Dependency(
            dependency.attrib["supplier"], dependency.attrib["comment"] if "comment" in dependency.attrib else None))

        for association in namespace_root.findall(_umlSchema + "Association"):
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

        return UMLData(tree, packages, elements, class_diagram_list, sequence_diagram_list)

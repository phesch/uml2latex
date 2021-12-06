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

"""Generates LaTeX class descriptions."""

import re

from uml2latex.tex.common import *
from uml2latex.utils import escape
from uml2latex.data import ElementType

def _make_class_header(clinfo):
    return """\t\t\\subsubsection{{{0}}}
			\\label{{{0}}}{1}\n""".format(clinfo.cl.name,
        "\n\t\t\t\\textbf{erbt von " + clinfo.ref(clinfo.cl.abstraction) + "}" \
            if clinfo.cl.abstraction is not None else "")

def _make_class_single_diagram(clinfo):
    return """\t\t\t\\begin{{center}}
				\\includegraphics[width=\\textwidth]{{{1}/Diagram_{0}.pdf}}
			\\end{{center}}\n""".format(clinfo.cl.name, clinfo.image_dir)

def _make_class_description(clinfo):
    return """\t\t\t{0}\n""".format(doc(clinfo.cl.docs, clinfo.cl.name))

def _make_class_template_list(clinfo):
    if clinfo.cl.template is None:
        return ""
    template = clinfo.elements[clinfo.cl.template]
    text = beginItem.format("Typparameter")
    ty = clinfo.ref(template.bound) if template.bound is not None else ""
    text += asItem.format(ty + template.name, doc(template.docs, template.name))
    text += endItem
    return text

def _make_class_operations_list(clinfo):
    if not clinfo.cl.operations:
        return ""
    text = beginItem.format("Operationen")
    for op in clinfo.cl.operations:
        opName = escape(op.attrib["name"])
        ret = "void"
        args = []
        if len(op) >= 1:
            for param in op[0]:
                ty = param.attrib["type"]
                if "kind" in param.attrib and param.attrib["kind"] == "return":
                    ret = clinfo.ref(ty) if ty in clinfo.elements else "Nested classes aren't supported."
                else:
                    args.append(escape(param.attrib["name"]) + ": " + clinfo.ref(ty) \
                        if ty in clinfo.elements else "Nested classes aren't supported.")
        text += asItem.format("{0} {1}({2})".format(ret, opName, ", ".join(args)),
            attrdoc(op.attrib, "comment", opName))
    text += endItem
    return text

def _make_class_attributes_list(clinfo):
    if not clinfo.cl.attributes:
        return ""
    text = beginItem.format("Attribute")
    for at in clinfo.cl.attributes:
        atName = escape(at.attrib["name"])
        ty = ""
        if "type" in at.attrib:
            ty = clinfo.ref(at.attrib["type"]) + " "
        text += asItem.format(ty + atName, attrdoc(at.attrib, "comment", atName))
    text += endItem
    return text

def _make_class_child_list(clinfo):
    if not clinfo.cl.children:
        return ""
    text = beginItem.format("Erbende Klassen")
    for child in clinfo.cl.children:
        text += "\t\t\t\t\t\\item \\texttt{{{0}}}\n".format(clinfo.ref(child))
    text += endItem
    return text

def _make_class_dependency_list(clinfo):
    if not clinfo.cl.dependencies:
        return ""
    text = beginItem.format("Abhängigkeiten")
    for dep in clinfo.cl.dependencies:
        text += asItem.format(clinfo.ref(dep.target), doc(dep.docs, "Abhängigkeit"))
    text += endItem
    return text

def _make_class_association_list(clinfo):
    if not clinfo.cl.associations:
        return ""
    text = beginItem.format("Assoziationen")
    for a in clinfo.cl.associations:
        multiplicity = a.multiplicity + " " if a.multiplicity is not None else ""
        text += asItem.format("{0}{1} {2}".format(multiplicity, clinfo.ref(a.target), a.name),
            doc(a.docs, a.name))
    text += endItem
    return text

class ClassInfo:
    """Holds information required to format a LaTeX class description.

    Attributes:
        class_description_template: (static) The template macro parameters and functions
            used for class description generation.
        cl: The class to be formatted.
        elements: The element dictionary of the project, required for references.
        noref: A set of elements not to create references to (because they would break).
        image_dir: The directory the class diagrams can be found in.
    """

    class_description_template = [
        ("%HEADER", _make_class_header),
        ("%DIAGRAM", _make_class_single_diagram),
        ("%DESCRIPTION", _make_class_description),
        ("%TEMPLATE", _make_class_template_list),
        ("%OPERATIONS", _make_class_operations_list),
        ("%ATTRIBUTES", _make_class_attributes_list),
        ("%CHILDREN", _make_class_child_list),
        ("%DEPENDENCIES", _make_class_dependency_list),
        ("%ASSOCIATIONS", _make_class_association_list),
    ]

    def __init__(self, cl, elements, noref, image_dir):
        self.cl = cl
        self.elements = elements
        self.noref = noref
        self.image_dir = image_dir

    def ref(self, element_name):
        """Generate a reference to the given element.

        Returns a LaTeX nameref string if the element can be referenced.
        Otherwise, it returns the element's name (with the template parameter given in '<>', if applicable)

        Args:
            element_name: The name of the element to reference.
        """
        element = self.elements[element_name]
        if element.ty == ElementType.CLASS and element.package != "std" and element.name not in self.noref:
            return "\\nameref{" + element.name + "}"
        else:
            # Match template classes with type parameter, both optionally prefixed by package::
            match = re.match("(?:\w+::)?(\w+)(?:<(?:\w+::)?(\w+)>)", element.name)
            if not match:
                return element.name
            else:
                return "{0}<{1}>".format(match.group(1), match.group(2))

def make_class_descriptions(tex_info):
    """Generate the descriptions for all the classes listed in the given info.

    Returns a string containing the appropriated LaTeX for the description list.
    TODO: Extract the hardcoded strings used for this generation into some kind
    of language file.

    Args:
        tex_info: The TexInfo to get required information from.
    """
    if not tex_info.packages:
        return ""
    text = "\\section{Klassenbeschreibungen}\n\t\\label{Klassenbeschreibungen}\n"
    text += tex_info.override.classes_desc
    for package, classes in tex_info.packages:
        text += """\t\\subsection{{{0}}}
		\\label{{{0}}}""".format(package.attrib["name"])
        for cl in classes:
            text += "%{0} template\n".format(cl.name)
            text += format_template(ClassInfo.class_description_template,
                    get(tex_info.override.classes, cl.name),
                    ClassInfo(cl, tex_info.elements, tex_info.override.noref, tex_info.image_dir))
        text += "\t\\newpage\n"
    return text

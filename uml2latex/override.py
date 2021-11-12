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

"""Code for reading in override files from a directory."""

import re
import glob

class Override:
    """Reads in override files from a directory and stores the information.

    See the main documentation for details on which overrides are available.

    Attributes:
        root: A macro string for the root of the generated document.
        diagram_order: A list of diagrams specifying their order.
        sequence_diagram_order. A list of sequence diagrams specifying their order.
        module_list_order: A list of modules specifying their order.
        noref: A set of element names that no links should be generated to.
        custom_width: A dict of class names and the width their diagrams should be generated with.
        architecture_desc: A description to be placed at the start of the architecture section.
        classes_desc: A description to be placed at the start of the class diagrams section.
        sequence_desc: A description to be placed at the start of the sequence diagrams section.
        module_order: A dict of module names and the order their classes should be listed in.
        module_listing: A dict of modules and macro strings for their sections.
        diagrams: A dict of diagrams and macro strings for their sections.
        classes: A dict of classes and macro strings for their sections.
    """

    def __init__(self, directory):
        self.root = ""
        self.diagram_order = []
        self.sequence_diagram_order = []
        self.module_list_order = []
        self.noref = set()
        self.custom_width = {}
        self.architecture_desc = ""
        self.classes_desc = ""
        self.sequence_desc = ""
        self.module_order = {}
        self.module_listing = {}
        self.diagrams = {}
        self.classes = {}

        for file in glob.glob("{}/*".format(directory)):
            filename = file.split("/")[-1]
            for (regex, func) in _files.items():
                match = re.match(regex, filename)
                if match:
                    with open(file, "r") as f:
                        func(self, match.groups(), f.read())

    def _override_root(self, match, text):
        self.root = text

    def _override_diagram_order(self, match, text):
        self.module_list_order = text.splitlines()

    def _override_sequence_diagram_order(self, match, text):
        self.sequence_diagram_order = text.splitlines()

    def _override_module_list_order(self, match, text):
        self.module_list_order = text.splitlines()

    def _override_no_ref(self, match, text):
        self.noref = set(text.splitlines())

    def _override_custom_width(self, match, text):
        self.custom_width = dict([tuple(l.split(" ")) for l in text.splitlines()])

    def _override_architecture_desc(self, match, text):
        self.architecture_desc = text

    def _override_classes_desc(self, match, text):
        self.classes_desc = text

    def _override_sequence_desc(self, match, text):
        self.sequence_desc = text

    def _override_module_order(self, match, text):
        self.module_order[match[0]] = text.splitlines()

    def _override_module_listing(self, match, text):
        self.module_listing[match[0]] = text

    def _override_diagrams(self, match, text):
        self.diagrams[match[0]] = text

    def _override_classes(self, match, text):
        self.classes[match[0]] = text

_files = {
        "%ROOT": Override._override_root,
        "%DIAGRAM_ORDER": Override._override_diagram_order,
        "%SEQUENCE_DIAGRAM_ORDER": Override._override_sequence_diagram_order,
        "%MODULE_ORDER": Override._override_module_list_order,
        "%NOREF": Override._override_no_ref,
        "%CUSTOM_WIDTH": Override._override_custom_width,
        "%ARCHITECTURE_DESC": Override._override_architecture_desc,
        "%CLASSES_DESC": Override._override_classes_desc,
        "%SEQUENCE_DESC": Override._override_sequence_desc,
        "([a-zA-Z][a-zA-Z0-9_]*)%ORDER": Override._override_module_order,
        "([a-zA-Z][a-zA-Z0-9_]*)%LISTING": Override._override_module_listing,
        "([a-zA-Z][a-zA-Z0-9_]*)%DIAGRAM": Override._override_diagrams,
        "([a-zA-Z][a-zA-Z0-9_]*)%CLASS": Override._override_classes
        }

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

"""Main entry point for uml2latex. Handles command line parameters."""

import argparse
import os
import sys
import glob
import tempfile
import subprocess

from uml2latex.utils import space_ul
from uml2latex.parse import UMLData
from uml2latex.diagrams import make_all_single_class_diagrams
from uml2latex.override import Override
from uml2latex.tex.generate import generate_latex

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
    make_all_single_class_diagrams(umlData.tree, umlData.elements, override.custom_width)

    if not args.no_pics:
        tmpfile, tmppath = tempfile.mkstemp(prefix="uml")
        umlData.tree.write(tmpfile, xml_declaration=True, encoding="utf-8")
        try:
            os.mkdir(args.outImages)
        except:
            pass
        # Unfortunately, umbrello can't output directly to PDF.
        subprocess.run(["umbrello5", "--directory", args.outImages, "--export", "svg", tmppath],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for file in glob.glob("{}/*.svg".format(args.outImages)):
            subprocess.run(("rsvg-convert \"" + file + "\" -f pdf > \"" +
                space_ul(file[:file.find("svg", -1) - 2]) + "pdf\""), shell=True)
            os.remove(file)
        os.remove(tmppath);

    latex = generate_latex(umlData, args.outImages, override)
    with get_output(args.output) as f:
        f.write(latex)

    return 0

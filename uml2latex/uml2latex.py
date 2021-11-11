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

    latex = generate_latex(umlData, args.outImages, override)
    with get_output(args.output) as f:
        f.write(latex)

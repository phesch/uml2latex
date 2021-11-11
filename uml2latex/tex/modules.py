# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

from uml2latex.tex.common import *
from uml2latex.tex.diagrams import DiagramInfo, make_diagram_image

def make_module_header(modinfo):
    return "\t\\subsection{{{0}}}\n".format(modinfo.module.attrib["name"])

def make_module_description(modinfo):
    return "\t\t{0}\n".format(attrdoc(modinfo.module.attrib, "comment", modinfo.module.attrib["name"]))

def make_module_classlist(modinfo):
    text = "\t\t\\subsubsection*{Klassen}\n"
    text += beginMultiColItem
    for cl in modinfo.classes:
        text += "\t\t\t\t\t\t\\item \\nameref{{{0}}}\n".format(cl.name)
    text += endMultiColItem
    return text

def make_module_diagram(modinfo):
    diagram = next((d for d in modinfo.diagrams \
            if d.attrib["name"].casefold() == modinfo.module.attrib["name"].casefold()), None)
    if diagram is not None:
        modinfo.diagrams.remove(diagram)
        return make_diagram_image(DiagramInfo(diagram, modinfo.image_dir))
    return ""

class ModuleInfo:
    module_template = [
        ("%HEADER", make_module_header),
        ("%DESCRIPTION", make_module_description),
        ("%CLASSLIST", make_module_classlist),
        ("%DIAGRAM", make_module_diagram),
    ]

    def __init__(self, module, classes, diagrams, image_dir):
        self.module = module
        self.classes = classes
        self.diagrams = diagrams
        self.image_dir = image_dir

def make_module_list(tex_info):
    text = tex_info.override.architecture_desc
    for package, classes in tex_info.packages:
        text += format_template(ModuleInfo.module_template,
                get(tex_info.override.module_listing, package.attrib["name"]),
                ModuleInfo(package, classes, tex_info.class_diagrams, tex_info.image_dir))
    return text

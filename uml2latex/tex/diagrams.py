# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

"""Generates LaTeX formatting for class and sequence diagrams."""

from uml2latex.tex.common import *
from uml2latex.utils import space_ul, escape

def _make_diagram_header(diagram_info):
    return """\t\\subsection{{{0}}}
		\\label{{{0}}}""".format((diagram_info.diagram.attrib["name"]))

def make_diagram_image(diagram_info):
    """Generate the formatting for a full-page diagram with its name on it.

    Returns the appropriate LaTeX formatting for a full-page diagram.

    Args:
        diagram_info: The DiagramInfo to generate the formatting with.
    """
    return """\t\t\\includepdf[landscape,pagecommand={{\\thispagestyle{{empty}}}},picturecommand={{
			\put(20, 30){{
				\\rotatebox{{90}}{{
					\\large \\bfseries {1}
				}}
			}}
		}}]
		{{{2}/{0}.pdf}}\n""".format(space_ul(diagram_info.diagram.attrib["name"]),
                escape(diagram_info.diagram.attrib["name"]), diagram_info.image_dir)

def _make_diagram_image_with_section(diagram_info):
    return """\t\\includepdf[landscape,addtotoc={{1,subsection,2,{1},{1}}},
		pagecommand={{\\thispagestyle{{empty}}}},
		picturecommand={{
			\put(20, 30){{
				\\rotatebox{{90}}{{
					\\large \\bfseries \\thesubsection\\hspace*{{1ex}}{1}
				}}
			}}
		}}]
		{{{2}/{0}.pdf}}""".format(space_ul(diagram_info.diagram.attrib["name"]),
                escape(diagram_info.diagram.attrib["name"]), diagram_info.image_dir)

def _make_diagram_description(diagram_info):
    return "\t\t{0}\n".format(
            attrdoc(diagram_info.diagram.attrib, "documentation", diagram_info.diagram.attrib["name"]))

class DiagramInfo:
    """Holds information required to format a class or sequence diagram in LaTeX.

    Attributes:
        diagram_template: (static) The template macro parameters and functions
            used for diagrams with descriptive text.
        diagram_no_desc_template: (static) The template macro parameters and functions
            used for diagrams without descriptive text.
        diagram: The diagram to be formatted.
        image_dir: The directory the diagram can be found in.
    """

    diagram_template = [
        ("%HEADER", _make_diagram_header),
        ("%DESCRIPTION", _make_diagram_description),
        ("%DIAGRAM", make_diagram_image),
    ]

    diagram_no_desc_template = [
        ("%DIAGRAM", _make_diagram_image_with_section),
    ]

    def __init__(self, diagram, image_dir):
        self.diagram = diagram
        self.image_dir = image_dir

def _make_diagrams(tex_info, diagrams):
    text = ""
    for diagram in diagrams:
        if diagram.attrib["documentation"] == "":
            text += format_template(DiagramInfo.diagram_no_desc_template,
                    get(tex_info.override.diagrams, diagram.attrib["name"]), 
                    DiagramInfo(diagram, tex_info.image_dir))
        else:
            text += format_template(DiagramInfo.diagram_template,
                    get(tex_info.override.diagrams, diagram.attrib["name"]),
                    DiagramInfo(diagram, tex_info.image_dir))
    return text

def make_sequence_diagrams(tex_info):
    """Generate the formatting for all the sequence diagrams listed in the given info.

    Returns a string containing the appropriate LaTeX for the sequence diagram section.
    TODO: Extract the hardcoded strings (see classes.py)

    Args:
        tex_info: The TexInfo to get required information from.
    """
    if not tex_info.sequence_diagrams:
        return ""
    text = "\\section{Abläufe}\n\t\\label{Abläufe}\n"
    text += tex_info.override.sequence_desc
    text += _make_diagrams(tex_info, tex_info.sequence_diagrams)
    return text

def make_class_diagrams(tex_info):
    """Generate the formatting for all the class diagrams listed in the given info.

    Returns a string containing the appropriate LaTeX for the sequence diagram section.
    TODO: Extract the hardcoded strings (see classes.py)
    TODO: Which class diagrams are rendered here is dependent on the ordering of the root macros.

    Args:
        tex_info: The TexInfo to get required information from.
    """
    if not tex_info.class_diagrams:
        return ""
    text = "\\section{Klassendiagramme}\n\t\\label{Klassendiagramme}\n"
    text += _make_diagrams(tex_info, tex_info.class_diagrams)
    text += "\\newpage\n"
    return text

# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

import xml.etree.ElementTree as ET
import re

from uml2latex.data import *

beginItem = """\t\t\t\\paragraph{{{0}}}
			\\begin{{itemize}}[label={{}}]\n"""
endItem = """\t\t\t\\end{itemize}\n"""
beginMultiColItem = """\t\t\t\\begin{multicols}{2}
					\\begin{itemize}[label={}, noitemsep]\n"""
endMultiColItem = """\t\t\t\t\t\\end{itemize}
			\\end{multicols}\n"""
asItem = """\t\t\t\t\\item {{
					\\raggedright
						\\hspace*{{-1cm}}
						\\texttt{{{0}}}\\\\
				}}
				{1}\n"""

def make_class_header(cl, element_dict, no_ref):
    return """\t\t\\subsubsection{{{0}}}
			\\label{{{0}}}{1}\n""".format(cl.name,
        "\n\t\t\t\\textbf{erbt von " + ref(element_dict[cl.abstraction], no_ref) + "}" \
            if cl.abstraction is not None else "")

def make_class_single_diagram(cl, element_dict, no_ref):
    return """\t\t\t\\begin{{center}}
				\\includegraphics[width=\\textwidth]{{outImages/Diagram_{0}.pdf}}
			\\end{{center}}\n""".format(cl.name)

def make_class_description(cl, element_dict, no_ref):
    return """\t\t\t{0}\n""".format(doc(cl.docs, cl.name))

def make_class_template_list(cl, element_dict, no_ref):
    if cl.template is None:
        return ""
    template = element_dict[cl.template]
    text = beginItem.format("Typparameter")
    ty = ref(element_dict[template.bound], no_ref) if template.bound is not None else ""
    text += asItem.format(ty + template.name, doc(template.docs, template.name))
    text += endItem
    return text

def make_class_operations_list(cl, element_dict, no_ref):
    if len(cl.operations) == 0:
        return ""
    text = beginItem.format("Operationen")
    for op in cl.operations:
        opName = escape(op.attrib["name"])
        ret = "void"
        args = []
        if len(op) >= 1:
            for param in op[0]:
                ty = param.attrib["type"]
                if "kind" in param.attrib and param.attrib["kind"] == "return":
                    ret = ref(element_dict[ty], no_ref) if ty in element_dict else "Es riecht nach genisteten Klassen."
                else:
                    args.append(escape(param.attrib["name"]) + ": " + ref(element_dict[ty], no_ref) \
                        if ty in element_dict else "Es riecht nach genisteten Klassen.")
        text += asItem.format("{0} {1}({2})".format(ret, opName, ", ".join(args)),
            attrdoc(op.attrib, "comment", opName))
    text += endItem
    return text

def make_class_attributes_list(cl, element_dict, no_ref):
    if len(cl.attributes) == 0:
        return ""
    text = beginItem.format("Attribute")
    for at in cl.attributes:
        atName = escape(at.attrib["name"])
        ty = ""
        if "type" in at.attrib:
            ty = ref(element_dict[at.attrib["type"]], no_ref) + " "
        text += asItem.format(ty + atName, attrdoc(at.attrib, "comment", atName))
    text += endItem
    return text

def make_class_child_list(cl, element_dict, no_ref):
    if len(cl.children) == 0:
        return ""
    text = beginItem.format("Erbende Klassen")
    for child in cl.children:
        text += "\t\t\t\t\t\\item \\texttt{{{0}}}\n".format(ref(element_dict[child], no_ref))
    text += endItem
    return text

def make_class_dependency_list(cl, element_dict, no_ref):
    if len(cl.dependencies) == 0:
        return ""
    text = beginItem.format("Abhängigkeiten")
    for dep in cl.dependencies:
        text += asItem.format(ref(element_dict[dep.target], no_ref), doc(dep.docs, "Abhängigkeit"))
    text += endItem
    return text

def make_class_association_list(cl, element_dict, no_ref):
    if len(cl.associations) == 0:
        return ""
    text = beginItem.format("Assoziationen")
    for a in cl.associations:
        multiplicity = a.multiplicity + " " if a.multiplicity is not None else ""
        text += asItem.format("{0}{1} {2}".format(multiplicity, ref(element_dict[a.target], no_ref), a.name),
            doc(a.docs, a.name))
    text += endItem
    return text

def make_module_header(module, classes, diagrams):
    return "\t\\subsection{{{0}}}\n".format(module.attrib["name"])

def make_module_description(module, classes, diagrams):
    return "\t\t{0}\n".format(attrdoc(module.attrib, "comment", module.attrib["name"]))

def make_module_classlist(module, classes, diagrams):
    text = "\t\t\\subsubsection*{Klassen}\n"
    text += beginMultiColItem
    for cl in classes:
        text += "\t\t\t\t\t\t\\item \\nameref{{{0}}}\n".format(cl.name)
    text += endMultiColItem
    return text

def make_module_diagram(module, classes, diagrams):
    diagram = next((d for d in diagrams if d.attrib["name"].casefold() == module.attrib["name"].casefold()), None)
    if diagram is not None:
        diagrams.remove(diagram)
        return make_diagram_diagram(diagram)
    return ""

def make_diagram_header(diagram):
    return """\t\\subsection{{{0}}}
		\\label{{{0}}}""".format((diagram.attrib["name"]))

def make_diagram_diagram(diagram):
    return """\t\t\\includepdf[landscape,pagecommand={{\\thispagestyle{{empty}}}},picturecommand={{
			\put(20, 30){{
				\\rotatebox{{90}}{{
					\\large \\bfseries {1}
				}}
			}}
		}}]
		{{outImages/{0}.pdf}}\n""".format(space_ul(diagram.attrib["name"]), escape(diagram.attrib["name"]))
    #return """\t\t\\begin{{center}}
	#		\\includegraphics[width=\\textwidth]{{outImages/{0}.pdf}}
	#	\\end{{center}}\n""".format(diagram.attrib["name"])

def make_diagram_diagram_with_section(diagram):
    return """\t\\includepdf[landscape,addtotoc={{1,subsection,2,{1},{1}}},
		pagecommand={{\\thispagestyle{{empty}}}},
		picturecommand={{
			\put(20, 30){{
				\\rotatebox{{90}}{{
					\\large \\bfseries \\thesubsection\\hspace*{{1ex}}{1}
				}}
			}}
		}}]
		{{outImages/{0}.pdf}}""".format(space_ul(diagram.attrib["name"]), escape(diagram.attrib["name"]))

def make_diagram_description(diagram):
    return "\t\t{0}\n".format(attrdoc(diagram.attrib, "documentation", diagram.attrib["name"]))

def make_module_list(default_templates, packages, diagrams, sequence_diagrams, element_dict, override, no_ref):
    #text = "\\section{Architektur}\n\t\\label{Architektur}\n"
    text = ""
    if "ARCHITECTURE_DESC" in override:
        text += override["ARCHITECTURE_DESC"]
    for package, classes in packages:
        text += format_template(default_templates["modules"], override,
            package.attrib["name"] + "_listing", package, classes, diagrams)
    return text

def make_manual_diagrams(default_templates, packages, diagrams, sequence_diagrams, element_dict, override, no_ref):
    if len(diagrams) == 0:
        return ""
    text = "\\section{Klassendiagramme}\n\t\\label{Klassendiagramme}\n"
    for diagram in diagrams:
        if diagram.attrib["documentation"] == "":
            text += format_template(default_templates["manual_diagrams_no_desc"], override,
                diagram.attrib["name"], diagram)
        else:
            text += format_template(default_templates["manual_diagrams"], override,
                diagram.attrib["name"], diagram)
    text += "\\newpage\n"
    return text

def make_class_descriptions(default_templates, packages, diagrams, sequence_diagrams, element_dict, override, no_ref):
    text = "\\section{Klassenbeschreibungen}\n\t\\label{Klassenbeschreibungen}\n"
    if "CLASSES_DESC" in override:
        text += override["CLASSES_DESC"]
    for package, classes in packages:
        text += """\t\\subsection{{{0}}}
		\\label{{{0}}}""".format(package.attrib["name"])
        for cl in classes:
            text += "%{0} template\n".format(cl.name)
            text += format_template(default_templates["class_descriptions"], override,
                cl.name, cl, element_dict, no_ref)
        text += "\t\\newpage\n"
    return text

def make_sequence_diagrams(default_templates, packages, diagrams, sequence_diagrams, element_dict, override, no_ref):
    if len(sequence_diagrams) == 0:
        return ""
    text = "\\section{Abläufe}\n\t\\label{Abläufe}\n"
    if "SEQUENCE_DESC" in override:
        text += override["SEQUENCE_DESC"]
    for diagram in sequence_diagrams:
        if diagram.attrib["documentation"] == "":
            text += format_template(default_templates["manual_diagrams_no_desc"], override,
                diagram.attrib["name"], diagram)
        else:
            text += format_template(default_templates["manual_diagrams"], override,
                diagram.attrib["name"], diagram)
    return text

def format_template(default_template, override, override_key, *args):
    segments = {"%FULL": ""}
    for entry, function in default_template:
        segments[entry] = function(*args)
        segments["%FULL"] += segments[entry]

    text = segments["%FULL"]
    if override_key in override:
        text = override[override_key]
        for segment, value in segments.items():
            text = text.replace(segment + "\n", value)
    return text

def ref(element, no_ref):
    if element.ty == ElementType.CLASS and element.package != "std" and element.name not in no_ref:
        return "\\nameref{" + element.name + "}"
    else:
        # Match template classes with type parameter, both optionally prefixed by package::
        match = re.match("(?:\w+::)?(\w+)(?:<(?:\w+::)?(\w+)>)", element.name)
        if not match:
            return element.name
        else:
            return "{0}<{1}>".format(match.group(1), match.group(2))

def doc(docs, name):
    return docs if docs is not None else "XXX Beschreibung von " + name + "."

def attrdoc(attribs, key, name):
    return attribs[key] if key in attribs else "XXX Beschreibung von " + name + "."

def sort_by_order(collection, order, func):
    sort_order = order.splitlines(keepends=False)
    sorted_list = []
    for name in sort_order:
        nxt = next((x for x in collection if func(x, name)), None)
        if nxt is not None:
            sorted_list.append(nxt)
    return sorted_list

def escape(text):
    return text.replace("_", "\\_").replace("&", "\\&").replace("$", "")

def space_ul(text):
    return text.replace(" ", "_")


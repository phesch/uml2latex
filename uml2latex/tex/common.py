# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

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

def format_template(default_template, override, tex_info):
    segments = {"%FULL": ""}
    for entry, function in default_template:
        segments[entry] = function(tex_info)
        segments["%FULL"] += segments[entry]

    text = segments["%FULL"]
    if len(override) > 0:
        text = override
        for segment, value in segments.items():
            text = text.replace(segment + "\n", value)
    return text

def get(dictionary, key):
    if key in dictionary:
        return dictionary[key]
    else:
        return ""

def doc(docs, name):
    return docs if docs is not None else "XXX Beschreibung von " + name + "."

def attrdoc(attribs, key, name):
    return attribs[key] if key in attribs else "XXX Beschreibung von " + name + "."

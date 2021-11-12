# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

"""Common strings and functions required to generate LaTeX templates."""

# {0}: The title of the itemize environment.
beginItem = """\t\t\t\\paragraph{{{0}}}
			\\begin{{itemize}}[label={{}}]\n"""
endItem = """\t\t\t\\end{itemize}\n"""
beginMultiColItem = """\t\t\t\\begin{multicols}{2}
					\\begin{itemize}[label={}, noitemsep]\n"""
endMultiColItem = """\t\t\t\t\t\\end{itemize}
			\\end{multicols}\n"""
# {0}: The title of the item, formatted as texttt.
# {1}: The description of the item.
asItem = """\t\t\t\t\\item {{
					\\raggedright
						\\hspace*{{-1cm}}
						\\texttt{{{0}}}\\\\
				}}
				{1}\n"""

def format_template(default_template, override, info):
    """Generate formatting based on a template.

    Replaces macros defined in default_template found in
    the override argument with the assigned function,
    called with the given info.

    The macro '%FULL' is always replaced with every function result
    defined in default_template in order.

    Args:
        default_template: A list of (macro string, function) pairs
            defining the macros and the texts to replace them with.
        override: The string to search for macros. If it is empty,
            it will be treated as containing only the macro '%FULL'.
        info: The argument to pass the functions in default_template.
    """
    segments = {"%FULL": ""}
    for entry, function in default_template:
        segments[entry] = function(info)
        segments["%FULL"] += segments[entry]

    text = segments["%FULL"]
    if len(override) > 0:
        text = override
        for segment, value in segments.items():
            text = text.replace(segment + "\n", value)
    return text

def get(dictionary, key):
    """Get the value for the given key from the dict, default to an empty string."""
    if key in dictionary:
        return dictionary[key]
    else:
        return ""

def doc(docs, name):
    """Return the given string if not none, otherwise a default string."""
    return docs if docs is not None else "XXX Beschreibung von " + name + "."

def attrdoc(attribs, key, name):
    """Return the attribs[key] value if defined, otherwise a default string."""
    return attribs[key] if key in attribs else "XXX Beschreibung von " + name + "."

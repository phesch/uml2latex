# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

"""Minor utilities required by multiple uml2latex components."""

def escape(text):
    """Escape a string for use as a literal in LaTeX."""
    return text.replace("_", "\\_").replace("&", "\\&").replace("$", "")

def space_ul(text):
    """Replace all paces in a string with underlines."""
    return text.replace(" ", "_")

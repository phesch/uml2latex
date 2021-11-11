# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

def escape(text):
    return text.replace("_", "\\_").replace("&", "\\&").replace("$", "")

def space_ul(text):
    return text.replace(" ", "_")

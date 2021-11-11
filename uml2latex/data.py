# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

from enum import Enum, auto

class ElementType(Enum):
    CLASS = auto()
    DATATYPE = auto()
    TEMPLATE = auto()
    DEPENDENCY = auto()
    ASSOCIATION = auto()

class ClassType(Enum):
    CLASS = auto()
    INTERFACE = auto()
    ENUM = auto()

class Class:
    ty = ElementType.CLASS

    def __init__(self, class_type, name, package, xmiId, operations, attributes, abstraction, template, docs, approx_height):
        self.class_type = class_type
        self.name = name
        self.package = package
        self.xmiId = xmiId
        self.operations = operations
        self.attributes = attributes
        self.abstraction = abstraction
        self.children = list()
        self.template = template
        self.docs = docs
        self.dependencies = list()
        self.associations = list()
        self.approx_height = approx_height

class DataType:
    ty = ElementType.DATATYPE

    def __init__(self, name, xmiId, docs):
        self.name = name
        self.xmiId = xmiId
        self.docs = docs

class Template:
    ty = ElementType.TEMPLATE

    def __init__(self, name, xmiId, bound, docs):
        self.name = name
        self.xmiId = xmiId
        self.bound = bound
        self.docs = docs

class Dependency:
    ty = ElementType.DEPENDENCY

    def __init__(self, target, docs):
        self.target = target
        self.docs = docs

class Association:
    ty = ElementType.ASSOCIATION

    def __init__(self, name, target, multiplicity, docs):
        self.name = name
        self.target = target
        self.multiplicity = multiplicity
        self.docs = docs

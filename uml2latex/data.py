# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

"""Defines data types parsed from the Umbrello XML format."""

from enum import Enum, auto

class ElementType(Enum):
    """The type of an element (something with an XMI ID we want to reference)"""

    CLASS = auto()
    DATATYPE = auto()
    TEMPLATE = auto()
    DEPENDENCY = auto()
    ASSOCIATION = auto()

class ClassType(Enum):
    """The subtype of a class element. Required for correct output generation."""
    CLASS = auto()
    INTERFACE = auto()
    ENUM = auto()

class Class:
    """A class defined in UML.

    Attributes:
        ty: (static) The ElementType of the class.
        class_type: The ClassType of the class.
        name: The class name.
        package: Which package the class is a member of.
        xmiId: The XMI ID of the class, used for references.
        operations: Functions and methods defined on the class.
        attributes: Attributes of the class.
        abstraction: Classes / interfaces the class inherits from.
        children: Classes that inherit from the class.
        template: Template parameters (generics) of the class.
        docs: Documentation associated with the class.
        dependencies: Objects the class depends on.
        associations: Objects the class is associated with.
        approx_height: An approximation for the height of the class in a UML diagram.
    """

    ty = ElementType.CLASS

    def __init__(self, class_type, name, package, xmiId, operations,
            attributes, abstraction, template, docs, approx_height):
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
    """A data type defined in UML.

    Usually used for members of libraries or other types
    that are only loosely defined.

    Attributes:
        ty: (static) The ElementType of data types.
        name: The name of the data type.
        xmiId: The XMI ID of the data type, used for references.
        docs: Documentation associated with the data type.
    """

    ty = ElementType.DATATYPE

    def __init__(self, name, xmiId, docs):
        self.name = name
        self.xmiId = xmiId
        self.docs = docs

class Template:
    """A template parameter defined in UML.

    Belongs to a single class.

    Attributes:
        ty: (static) The ElementType of template parameters.
        name: The name of the parameter.
        xmiId: The XMI ID of the template parameter, used for references.
        bound: A bound placed on the template parameter.
        docs: Documentation associated with the template parameter.
    """

    ty = ElementType.TEMPLATE

    def __init__(self, name, xmiId, bound, docs):
        self.name = name
        self.xmiId = xmiId
        self.bound = bound
        self.docs = docs

class Dependency:
    """A dependency defined in UML.

    Belongs to a class.

    A classes that depends on another isn't directly associated,
    but uses the other indirectly and thus requires the other's presence.

    Attributes:
        ty: (static) The ElementType of dependencies.
        target: The target of the dependency.
        docs: Documentation associated with the dependency.
    """

    ty = ElementType.DEPENDENCY

    def __init__(self, target, docs):
        self.target = target
        self.docs = docs

class Association:
    """An association defined in UML.

    Belongs to a class.

    Attributes:
        ty: (static) The ElementType of associations.
        name: The name of the association.
        target: The target of the association.
        multiplicity: The multiplicity of the association.
            See the UML spec for details.
        docs: Documentation associated with the association.
    """

    ty = ElementType.ASSOCIATION

    def __init__(self, name, target, multiplicity, docs):
        self.name = name
        self.target = target
        self.multiplicity = multiplicity
        self.docs = docs

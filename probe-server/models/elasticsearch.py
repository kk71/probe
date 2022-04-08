# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseESDoc",
    "BaseESInnerDoc",
    "InnerDoc",
    "ESObject",
    "ESNested",
    "ESDate",
    "ESBoolean",
    "ESKeyword",
    "ESText",
    "ESInteger",
    "ESFloat"
]


from elasticsearch_dsl import Document, InnerDoc, \
    Date as ESDate, \
    Nested as ESNested, \
    Object as ESObject, \
    Boolean as ESBoolean, \
    Keyword as ESKeyword, \
    Text as ESText, \
    Integer as ESInteger, \
    Float as ESFloat


class BaseESDoc(Document):
    """base elasticsearch document"""

    pass


class BaseESInnerDoc(InnerDoc):
    """base elasticsearch inner document"""

    pass

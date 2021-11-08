__author__ = "Rob MacKinnon <rome@villagertech.com>"
__package__ = "DOMObjects"
__name__ = "DOMObjects.schema"
__license__ = "MIT"


class DOMSchema(object):
    """ @abstract Structure object for creating more advanced DOM trees
        @params children [dict] Default structure of children
        @params dictgroups [dict] Default structure of dictgroups
        @params props [dict] Default structure of properties
        @example Sample object
            _schema = DOMSchema()
            _schema.children=

        _settings_schema.children = {
            "sip": {},
            "schedules": {},
            "favorites": {
                "dictgroups": ["sip", "http"]
            }
        }
    """
    def __init__(self,
                 children: dict = {},
                 dictgroups: dict = {},
                 props: dict = {}):
        """ @abstract Object initializer and bootstraps first object.
            @params children [dict] Default structure of children
            @params dictgroups [dict] Default structure of dictgroups
            @params props [dict] Default structure of properties
            @returns [DOMSchema] object
        """
        self.dictgroups = dictgroups
        self.children = children
        self.props = props

    @property
    def keys(self) -> list:
        """ @abstract Returns all top-level keys in schema
            @returns [list] of keys
        """
        _keys = list()
        _keys.extend(self.children.keys())
        _keys.extend(self.dictgroups.keys())
        _keys.extend(self.props.keys())
        return _keys

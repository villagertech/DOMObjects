from collections.abc import MutableMapping
from warnings import warn

__author__ = "Rob MacKinnon <rome@villagertech.com>"
__package__ = "DOMObjects"
__name__ = "__init__"
__version__ = "0.1.0b4"
__license__ = "MIT"

__doc__ = """
See README.md for documentation and CHANGES.md
"""

from .flags import (
    DOMFlags,
    FLAG_READ,
    FLAG_WRITE,
    FLAG_NAMESPACE,
    FLAG_RESERVED_8,
    FLAG_RESERVED_16,
    FLAG_RESERVED_32,
    FLAG_RESERVED_64,
    FLAG_RESERVED_128
)

from .schema import (
    DOMSchema
)

# INTERNAL DEBUGGING FLAG, not for production consumption.
DEBUG = 0


class DOMObject(object):
    """ @abstract: This object is used to create new DOM object data
            structures allowing traversable objects trees similar to
            Javascript DOM objects.
    """
    def __init__(self, name: str):
        """ @abstract Base DOM object initializer
            @param name [str] DOM object name
            @returns [None]
        """
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "parent", None)
        object.__setattr__(self, "__flags__", DOMFlags())
        # Override for DictGroup storage of child type
        object.__setattr__(self, "__store__", self.__dict__)

        self.__flags__.set_flag("parent", 0 | FLAG_READ | FLAG_WRITE)
        self.__children__ = []
        self.__properties__ = []

    def __setattr__(self, name: str, value: object) -> None:
        """ @abstract `__setattr__` method override to allow for dynamic
                setting of child properties and methods.
            @param name [str] Object name
            @param value [object] Callable/referenceable object
            @returns [None]
        """
        if ((name not in self.__store__ and not self.__protected__) or
           self.__flags__.is_writeable(name)):
            self.__store__[name] = value
            self.__flags__.set_flag(name=name, flags=0 | FLAG_READ | FLAG_WRITE)
        elif self.__protected__ or not self.__flags__.is_writeable(name):
            raise KeyError("node rights for `%s` are locked" % name)
        else:
            raise(KeyError("property `%s` not set" % name))

        self.__store__[name] = value

    # Private properties
    @property
    def __protected__(self) -> bool:
        """ @abstract Wrapper to Bit Flag `protected` prop
            @returns [bool] See [DOMFlag.protected] property
        """
        return self.__flags__.protected

    # Private methods
    def __new_child__(cls, name) -> object:
        """ @abstract Anonymous new child DOMObject
            @returns [DOMObject] New anonymous object
        """
        _instance = super(DOMObject, cls).__new__(DOMObject)
        _instance.__init__(name)
        return _instance

    def __new_dictgroup__(cls, name) -> object:
        """ @abstract Anonymous new child DOMObject
            @returns [DOMObject] New anonymous object
        """
        _instance = super(DictGroup, cls).__new__(DictGroup)
        _instance.__init__(name)
        return _instance

    def __child__(self, name) -> object:
        """ @abstract Private child reference for individual child nodes.
            @param name [str] DOM object name
            @returns [object] Referenced child object
        """
        assert name in self.__children__
        return self.__store__[name]

    def __name_exists__(self, name: str) -> bool:
        """ @abstract Private check for testing name availability
            @param name [str] DOM object name
            @returns [bool] True on exists
        """
        if DEBUG == 1:
            print("name exists '%s' = %s" % (name, name in self.__store__))
        return name in self.__store__

    def __update_parent__(self, instance: object, parent: object) -> None:
        """ @abstract Update the parent of an object
            @param instance [DOMObject] Instance of object to update
            @param parent [DOMObject] Parent instance to point to
        """
        instance.__flags__.unlock("parent")
        instance.parent = parent
        instance.__flags__.lock("parent")

    # Public Properties
    @property
    def children(self) -> list:
        """ @abstract Property to return all current children names
            @returns [list] List of all children names
        """
        return self.__children__

    @property
    def siblings(self) -> list:
        """ @abstract Property to return all current sibling names
            @returns [list] List of all sibling names
        """
        if ((self.parent is None) or
           (self.__flags__.test_bit("self", FLAG_NAMESPACE - 1) is not True)):
            _siblings = list(self.parent.children)
            _siblings.remove(self.name)
            _siblings.sort()
            if DEBUG == 1:
                print("self.name='%s'" % self.name)
                print("parent.children=%s" % self.parent.children)
                print("siblings(%s)=%s" % (type(_siblings), _siblings))
        else:
            _siblings = [self.name]
        return _siblings

    @property
    def props(self) -> list:
        """ @abstract Property to return all assigned node properties
            @returns [list] List of all assigned properies
        """
        return self.__properties__

    @property
    def path(self) -> str:
        """ @abstract Returns a nodes full object path
            @returns [str] Object named path

            @note path may contain invalid charactes or '.'
        """
        if ((self.parent is None) or
           (self.__flags__.test_bit("self", FLAG_NAMESPACE - 1))):
            return self.name
        return self.parent.path + '.' + self.name

    # Public Methods
    def dict(self, props: list = None, propsOnly: bool = False) -> dict:
        """ @abstract Built-in override to provide a static dictionary as
                output.
            @param props [list] #optional List of specific properties to return
            @param propsOnly [bool] #optional Should only properties be returned
            @returns [dict] Static dictionary object
        """
        _children = self.__children__
        if props == None:
            _propNames = self.__properties__
        else:
            _propNames = props
            for _prop in _propNames:
                # print("%s " % _prop, self.has_property(_prop))
                if not self.has_property(_prop):
                    raise KeyError("property `%s` is not defined." % _prop)
        _dict = {}
        for _prop in _propNames:
            if self.has_property(_prop):
                if callable(getattr(self, _prop)):
                    _ret = getattr(self, _prop)()
                else:
                    _ret = self.get_property(_prop)
            else:
                _ret = getattr(self, _prop)

            if callable(_ret):
                _ret = _ret()
            _dict.update({_prop: _ret})

        if not propsOnly:
            for _child in _children:
                _dict.update({_child: getattr(self, _child).dict()})

        return _dict

    def json(self, props: list = None, propsOnly: bool = False) -> str:
        """ @abstract Built-in to provide JSON as output.
            @param None
            Optional:
            @param props [list] #optional list of specific properties to return
            @param propsOnly [bool] #optional Should only properties be returned
            @returns [str] JSON text object
        """
        from json import dumps as JSON_DUMPS

        _retDict = self.dict(props=props, propsOnly=propsOnly)
        _ret = JSON_DUMPS(_retDict)
        del JSON_DUMPS
        return _ret

    def has_child(self, name: str) -> bool:
        """ @abstract Checks if name exists in children list
            @param name [str] DOM object name
            @returns [bool] True if exists in list
        """
        return name in self.children

    def has_property(self, prop: str) -> bool:
        """ @abstract Check if property exists
            @param name [str] DOM object name
            @returns [bool] True if exists in list
        """
        return prop in self.__properties__

    def attach(self, name: str = None,
               obj: object = None,
               flags: int = 0 | FLAG_READ | FLAG_WRITE) -> None:
        """ @abstract Attach a child object, and set flags to read/write
            @param name [str] DOM object name
            @param obj [object] callable/referable object
            @param flags [byte] byte mask of flags
            @returns [None]
        """
        assert not self.__flags__.protected
        assert not self.__name_exists__(name)

        if isinstance(obj, DOMObject):
            self.__update_parent__(instance=obj, parent=self)

        self.__store__[name] = obj
        self.__children__.append(name)
        self.__flags__.set_flag(name, flags)

    def detach(self, name: str) -> None:
        """ @abstract Remove a child object from tree structure
            @param name [str] DOM object name
            @returns [None]
        """
        assert not self.__flags__.protected
        assert self.__name_exists__(name)
        del self.__store__[name]
        self.__children__.remove(name)

    def new_property(self, propName: str,
                     propValue: object,
                     flags: int = 0 | FLAG_READ | FLAG_WRITE) -> None:
        """ @abstract Add a static property to self
            @param propName [str] DOM property name
            @param propValue [object] valued object
            @param flags [byte] byte mask of flags
            @returns [None]
        """
        assert (not self.__flags__.protected)
        if self.__name_exists__(propName):
            raise(AssertionError("property '%s' exists" % propName))
        self.__store__.update({propName: propValue})
        self.__properties__.append(propName)
        self.__flags__.set_flag(propName, flags)

    def del_property(self, propName: str) -> None:
        """ @abstract Remove property from self
            @param name [str] DOM property name
            @returns [None]
        """
        assert (not self.__flags__.protected)
        if not self.__name_exists__(propName):
            raise(AssertionError("property '%s' does not exists" % propName))
        del self.__store__[propName]
        self.__properties__.remove(propName)
        self.__flags__.del_flag(propName)

    def set_property(self, propName: str, propValue: object) -> None:
        """ @abstract Set the value of a property by name
            @param propName [str] Property name to set
            @param propValue [object] Value to set to property
            @returns [None]
        """
        if not self.__name_exists__(propName):
            warn("Attempted to set non-existent property '%s', running `new_property` method." % propName)
            self.new_property(propName, propValue)
        else:
            assert (self.__flags__.test_bit(propName, FLAG_WRITE) is True)
            self.__store__[propName] = propValue

    def new_method(self, name: str,
                     method: object,
                     margs: list = [],
                     mkwargs: list = {},
                     flags: int = 0 | FLAG_READ | FLAG_WRITE) -> None:
        """ @abstract Add a property method to self
            @param name [str] DOM property name
            @param method [object] Method to attach
            @param margs [list] Method arguments to pass
            @param flags [byte] byte mask of flags
            @returns [None]
        """
        assert (not self.__flags__.protected)
        if self.__name_exists__(name):
            raise(AssertionError("property method '%s' exists" % name))
        self.__store__.update({name: lambda: method(*margs, **mkwargs)})
        self.__properties__.append(name)
        self.__flags__.set_flag(name, flags)

    def set_method(self, name: str,
                   method: object,
                   margs: list, mkwargs: dict) -> None:
        """ @abstract Set the value of a property method by name
            @param name [str] DOM property name
            @param method [object] Method to attach
            @param margs [list] Method arguments to pass
            @returns [None]
        """
        if not self.__name_exists__(name):
            warn("Attempted to set non-existent property method '%s', running `new_method` method." % name)
            self.new_method(*args, **kwargs)
        else:
            assert (self.__flags__.test_bit(name, FLAG_WRITE) is True)
            self.__store__[name] = lambda: method(*margs, **mkwargs)

    def get_property(self, propName: str) -> object:
        """ @abstract Retrieve a specific property by name.
            @param propName [str] Property to retrieve.
            @returns [object]
        """
        if not self.__name_exists__(propName):
            raise(AssertionError("property '%s' does not exist" % propName))
        assert (self.__flags__.test_bit(propName, FLAG_READ) is True)
        return self.__store__[propName]

    def new_property_bulk(self, props: list) -> None:
        """ @abstract Add property to self in bulk
            @param props [list] List of property tuple name|value or name only
            @example Bulk Props Definition
                props = ["propName" | ("propName", value)]

                Note: defined properties with out value default to a value
                        of None
            @returns [None]
        """
        assert not self.__flags__.protected
        _value = None
        for _n in props:
            if isinstance(_n, tuple):
                _name = _n[0]
                try:
                    _value = _n[1]
                except KeyError:
                    raise KeyError(L10N_MESSAGES["DOM_ADD_PROP_EXCEPT_NAME_TUPLE_LEN"])
            else:
                _name = _n
            self.new_property(_name, _value)

    def new_child(self, name: str) -> None:
        """ @abstract Add child object to tree
            @param name [str] Child object name, name must conform to standard
                python variable naming schemes.
            @returns [None]
        """
        if self.__name_exists__(name):
            raise(AssertionError("child '%s' exists" % name))
        _instance = self.__new_child__(name)
        self.attach(name=name, obj=_instance)

    def del_child(self, name: str) -> None:
        """ @abstract Remove a child object from a tree
            @param name [str] Child object name, name must conform to standard
                python variable naming schemes.
            @returns [None]
        """
        if not self.__name_exists__(name):
            raise(AssertionError("child '%s' doesn't exists" % name))
        assert not self.__store__[name].__flags__.protected
        self.__store__.pop(name)

    def replace_child(self, name: str, new_child_obj: object) -> None:
        """ @abstract Replace and existing child object with provided object
            @param name [str] Existing child object name, name must conform to
                standard python variable naming schemes.
            @param new_child_obj [object] Replacement child object
            @returns [None]
        """
        self.del_child(name=name)
        self.attach(name=name, obj=new_child_obj)

    def new_namespace(self, name: str) -> None:
        """ @abstract Add child object of type namespace to tree
            @param name [str] Child object name, name must conform to standard
                python variable naming schemes.
            @returns None
        """
        if self.__name_exists__(name):
            raise(AssertionError("child '%s' exists" % name))
        _instance = self.__new_child__(name)
        self.__update_parent__(instance=_instance, parent=self)
        _instance.__flags__.update_flag("self", FLAG_NAMESPACE)
        self.attach(name=name, obj=_instance)

    def new_child_bulk(self, nameList: list) -> None:
        """ @abstract Add child object to tree in bulk
            @param nameList [list] List of child object names, names
                must conform to standard python variable naming schemes.
            @returns [None]
        """
        for _n in nameList:
            self.new_child(_n)

    def get_context(self, name: str = None) -> object:
        """ @abstract Get the context of a specific context
            @param name [str] Named contexted and path to return from object
            @returns [DOMObject] Node object of child
        """
        if name is None:
            return self
        if "." in name:
            _keys = name.split('.')
            assert self.__name_exists__(_keys[0])
            return self.__store__[_keys[0]].get_context('.'.join(_keys[1:]))
        else:
            assert self.__name_exists__(name)
            return self.__store__[name]

    def new_dictgroup(self, name: str) -> None:
        """ @abstract Add child object to tree
            @param name [str] Child object name, name must conform to standard
                python variable naming schemes.
            @returns [None]
        """
        if self.__name_exists__(name):
            raise(AssertionError("child '%s' exists" % name))
        _instance = DictGroup(parent=self, name=name)
        self.attach(name=name, obj=_instance)

    def new_dictgroup_bulk(self, nameList: list) -> None:
        """ @abstract Add child dictgroup objects to tree in bulk
            @param nameList [list] List of child object names, names
                must conform to standard python variable naming schemes.
            @returns [None]
        """
        for _n in nameList:
            self.new_dictgroup(_n)

    def build_prop_map(self, schema_map: list = []) -> None:
        """ @abstract Build a property tree from a defined schema and name map.
                This is designed for properties values only.
            @param schema_map [list] List of tuples, defining dict, and child
                name
            @returns [None]

            @example Object Schema and Mapping [dict]
            schema = {
                "<child_name>": {
                    "<attribute_name>": {
                        "cast": <type>,
                        "default": <value>
                        "values": [<value>, ...]
                        "validate_callback": <callable>
                    }
                }
            }

            schema_map = [
                (schema["<child_name>"], "<child_name>"), ...
            ]
        """
        for _map, _sect in schema_map:
            _ctx = self
            if _sect is not None:
                _ctx.new_child(_sect)
                _ctx = _ctx.get_context(_sect)
            for _key in _map:
                if "cast" not in _map[_key]:
                    continue

                _value = _map[_key]["cast"]()
                if "default" in _map[_key]:
                    _value = _map[_key]["default"]

                _ctx.new_property(_key, _value)

    def build_schema(self, schemaObj: DOMSchema) -> None:
        """ @abstract Build an object based on the structure stated
                by the schema object.
            @param schemaObj [DOMSchema] Structure to create.
            @returns [None]
        """
        def __build_props(propDict: dict,
                          ctx: object) -> None:
            """ @abstract Wrapper for contextual `build_prop_map`"""
            ctx.build_prop_map([(propDict, None)])

        def __build_dictgroup(groupDict: list,
                              ctx: object) -> None:
            """ @abstract Wrapper for contextual `new_dictgroup_bulk`"""
            ctx.new_dictgroup_bulk(groupDict)

        def __build_children(childDict: list,
                             ctx: object) -> None:
            """ @abstract Wrapper for contextual `new_child_bulk`"""
            ctx.new_child_bulk(childDict)

        def __recurse(node: dict,
                      workType: str = None,
                      ctx: object = None) -> None:
            """ @abstract Recurse builder of schema objects
                @params node [dict] object containing key name level
                @params workType
            """
            _recurseWork = {
                "children": __build_children,
                "dictgroups": __build_dictgroup,
                "props": __build_props
            }

            # generate all the keys of type(x) in the node
            if ((workType != None) and
                (workType in ["children", "dictgroups"])):
                _recurseWork[workType](node.keys(), ctx)

                for _key in node:
                    for _recWorkType in _recurseWork:
                        if _recWorkType in node[_key]:
                            __recurse(ctx=ctx.get_context(_key),
                                      node=node[_key][_recWorkType],
                                      workType=_recWorkType)
            elif ((workType != None) and
                  (workType == "props")):
                # Props is a leaf node
                _recurseWork[workType](node, ctx)

            else:
                # workType is None or not in ["children", "dictgroups", "props"]
                warn("Schema key `%s` not supported." % _workType)

        __recurse(ctx=self, node=schemaObj.children, workType="children")
        __recurse(ctx=self, node=schemaObj.dictgroups, workType="dictgroups")

        if len(schemaObj.props.keys()) > 0:
            __build_props(schemaObj.props, self)


class DOMRootObject(DOMObject):
    """ @abstract Create a root DOM object, with a top-level namespace.
    """
    def __init__(self):
        super(DOMRootObject, self).__init__("root")


class DictGroup(MutableMapping, DOMObject):
    """ @abstract Create a dictgroup DOM object.
        @param parent [DOMObject] Assign a parent object
        @param name [str] Object unique name
    """
    def __init__(self, parent: object = None, name: str = ""):
        super(DictGroup, self).__init__(name)

        if parent.__name_exists__(name):
            raise(AssertionError("child '%s' exists at parent." % name))
        object.__setattr__(self, "parent", parent)
        self.__keystore__ = dict()

    def __getitem__(self, key: str) -> object:
        """ @abstract Parallel of dict.__getitem___ method
            @param key [str] Key name to retrieve
            @returns object
        """
        return self.__keystore__[key]

    def __setitem__(self, key: str, value: object) -> None:
        """ @abstract Parallel of dict.__setitem___ method
            @param key [str] Key name to add
            @param value [object] Value object to attach to key
            @returns None
        """
        if isinstance(value, DOMObject):
            self.__update_parent__(instance=value, parent=self)
        self.__keystore__[key] = value

    def __delitem__(self, key: str) -> None:
        """ @abstract Parallel of dict.__delitem___ method
            @param key [str] Key name to remove
            @returns None
        """
        del self.__keystore__[key]

    def __iter__(self) -> MutableMapping:
        """ @abstract Parallel of dict.__iter___ method
            @returns [object] Returns iter object
        """
        return iter(self.__keystore__)

    def __len__(self) -> int:
        """ @abstract Parallel of dict.__len___ method
            @returns [int] Number of keys contained in keystore
        """
        return len(self.__keystore__)

    def __contains__(self, key: str) -> bool:
        """ @abstract Parallel of dict.__contains___ method
            @param key [str] Key name to check
            @returns [bool] True on key contained in keystore
        """
        return self.__keystore__.__contains__(key)

    def keys(self) -> list:
        """ @abstract Override to provide key list for dict style object
            @returns [list] of key names
        """
        return self.__keystore__.keys()

    def attach(self, name: str = None,
               obj: object = None,
               flags: int = 0 | FLAG_READ | FLAG_WRITE) -> None:
        """ @abstract Override of DOMObject.attach
            @param name [str] dict key name
            @param obj [object] callable/referable object
            @param flags [byte] byte mask of flags
            @returns [None]
        """
        assert not self.__flags__.protected
        assert not self.__name_exists__(name)

        if isinstance(obj, DOMObject):
            self.__update_parent__(instance=obj, parent=self)

        self.update({name: obj})
        self.__store__[name] = self.__keystore__[name]
        self.__children__.append(name)
        self.__flags__.set_flag(name, flags)

    def detach(self, name: str) -> None:
        """ @abstract Override of DOMObject.deattach
            @param name [str] dict child object name
            @returns [None]
        """
        assert not self.__flags__.protected
        assert self.__contains__(name)
        if name in self.__store__:
            del self.__store__[name]
        del self.__keystore__[name]
        if name in self.__children__:
            self.__children__.remove(name)

    def update(self, *args, **kwargs) -> None:
        """ @abstract Override for dict.update, manages DOMObjects better
            @examples Usage
                self.update({key: value, ...})  # Update a dict to the keystore
                self.update(<key>, <value>)     # Update a single key/value
                                                # pair to the keystore
                self.update(key1=value1, ...)   # Update a dict using keyword
                                                # key/value pairs
            @params key [str] Key name to use in keystore
            @params value [object] Value object to attach to key
            @params [dict] Dict object to insert into keystore
        """
        if isinstance(args[0], dict):
            self.__keystore__.update(args[0])

        elif (isinstance(args[0], str) and isinstance(args[1], DOMObject)):
            self.__setitem__(key=args[0], value=args[1])

        elif (kwargs.__len__() > 0):
            for _key, _value in kwargs.items():
                self.__setitem__(key=_key, value=_value)

        else:
            self.__keystore__.update(dict(*args, **kwargs))

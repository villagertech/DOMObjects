from collections.abc import MutableMapping

__author__ = "Rob MacKinnon <rome@villagertech.com>"
__package__ = "PyDOM"
__name__ = "__init__"
__version__ = "0.1.0b0"
__license__ = "MIT"

__doc__ = """
See README.md for documentation and CHANGES.md
"""

FLAG_READ = 2**0
FLAG_WRITE = 2**1
FLAG_NAMESPACE = 2**2
FLAG_RESERVED_8 = 2**3
FLAG_RESERVED_16 = 2**4
FLAG_RESERVED_32 = 2**5
FLAG_RESERVED_64 = 2**6
FLAG_RESERVED_128 = 2**7

DEBUG = 0


class DOMFlags(object):
    """ @abstract Class object for holding user definable flags for DOM Objects
    """
    def __init__(self):
        """ @abstract Object initializer and bootstraps first object.
        """
        self.__flags__ = {}
        self.default_flags = 0 | FLAG_READ | FLAG_WRITE
        self.__flags__["self"] = self.default_flags

    def __hasbit__(self, byteVal: int, bit: int = 0) -> bool:
        """ @abstract Private method to test if bit flag is set.
            @param byteVal [int] Binary flag set
            @param bit [int] Bit position to check true
            @returns [bool] True if bit value is 1
        """
        if DEBUG is 1:
            print("1?"+str(self.__getbit__(byteVal, bit))+" "+str(self.__getbit__(byteVal, bit) is 1))
        return self.__getbit__(byteVal, bit) is 1

    def __getbit__(self, byteVal: int, bit: int = 0) -> int:
        """ @abstract Returns the value of selected bit via bitwise operation
            @param byteVal [int] Binary flag set
            @param bit [int] Bit position to return
            @returns [int] 0|1 of value at bit position
        """
        assert 0 <= bit < 8
        _mask = 254

        if DEBUG is 1:
            _print = ""
            _marker = ""
            _value = ""
            for x in range(0, 8):
                _print += str(((byteVal >> x) | _mask) - _mask)
                if bit-1 is x:
                    _marker += "^"
                    _value += str(bit)
                else:
                    _marker += " "
                    _value += " "
            print(_print)
            print(_marker)
            print(_value)
        return ((byteVal >> bit-1) | _mask) - _mask

    def __setbit__(self, byteVal: int, bit: int = 0, value: int = 0) -> int:
        """ @abstract Set explicit bit value of flag
            @param byteVal [int] Byte value to modify
            @param bit [int] Bit position alter
            @param value [int] 0|1 value to alter to
            @returns [int] 0|1 of value at bit position
        """
        assert -1 < bit < 8
        assert -1 < value < 2

        # @bug Suddenly, a wild `None` appeared!
        #   We are not sure why DOMObject.attach() started setting the
        #   parent flag value to `None`, nor where it is actually doing
        #   so after an hour stepping through things. Below is the fix.
        if byteVal == -1:
            return self.default_flags

        _retVal = byteVal
        _bitVal = self.__getbit__(byteVal, bit)
        if _bitVal == value:
            # NOP
            pass
        elif _bitVal < value:
            _retVal = byteVal | 2**bit
        elif _bitVal > value:
            _retVal = byteVal - 2**bit
        else:
            raise Exception("we got somewhere we shouldn't have")
        return _retVal

    def has_flag(self, name: str) -> bool:
        """ @abstract Checks if `name` is a valid flag
            @param name [str] Flag key name to resolve
            @returns [bool] True on found/existing
        """
        return name in self.__flags__.keys()

    @property
    def protected(self) -> bool:
        """ @abstract Returns whether the parent is currently protected
            @returns [bool] True if write flag is 0
        """
        return not self.is_writeable(name="self")

    def is_writeable(self, name: str = "self") -> bool:
        """ @abstract Returns whether the object is currently protected
            @returns [bool] True if write flag is 1
        """
        if not self.has_flag(name):
            raise Exception("invalid flag name `%s` referenced" % name)
        if DEBUG is 1:
            print("hasbit="+str(self.__hasbit__(self.__flags__[name],
                                FLAG_WRITE)))
        return self.__hasbit__(self.__flags__[name], FLAG_WRITE)

    def lock(self, name: str = "self") -> None:
        """ @abstract Set the writeable flag to readonly
            @param name [str] Flag name
            @returns [None]
        """
        if not self.has_flag(name):
            raise Exception("invalid flag name referenced")
        self.__flags__[name] = self.__setbit__(self.__flags__[name],
                                               FLAG_WRITE, 0)

    def unlock(self, name: str = "self") -> None:
        """ @abstract Set the writeable flag to readonly
            @param name [str] Flag name
            @returns [None]
        """
        if not self.has_flag(name):
            raise KeyError("invalid flag name referenced")
        self.__flags__[name] = self.__setbit__(self.__flags__[name],
                                               FLAG_WRITE, 1)

    def test_bit(self, name: str, flag: int) -> bool:
        """ @abstract Boolean test for flag currently set
            @param name [str; Flag name
            @param flag [int] Bit position or FLAG_xxxxx global
            @returns [bool] True is requested value is set
        """
        return self.__hasbit__(self.get_flag(name), flag)

    def get_flag(self, name: str) -> int:
        """ @abstract Return the value of flag
            @param name:   str; flag name
            @returns [int] Byte value of flag set
        """
        if not self.has_flag(name):
            raise Exception("invalid flag name referenced")
        return self.__flags__[name]

    def set_flag(self, name: str, flags: int = 0) -> bool:
        """ @abstract Set a new flag with a specific bit flag
            @param name [str] Flag name
            @param flags [int] #optional Bit mask to set to
            @returns [bool] True on success
        """
        # Check to see if this flag already exists
        if self.has_flag(name):
            # flag name already exists, update instead
            return self.update_flag(name, flags)

        # Is this flag set protected, if not we should set the flags requested.
        if not self.protected:
            self.__flags__.update({name: flags})
            return True
        raise Exception("cannot add flag, parent locked")

    def del_flag(self, name: str) -> bool:
        """ @abstract Remove a flag
            @param name [str] Flag name
            @returns [bool] True on success
        """
        # Is this flag set protected, if not we should set the flags requested.
        if not self.protected:
            del self.__flags__[name]
            return True
        raise Exception("cannot delete flag, parent locked")

    def update_flag(self, name: str, flags: int) -> bool:
        """ @abstract update a flag to specified flag value
            @param name [str] Flag name
            @param flags [int] Bit mask to set
            @returns [bool] True on success
        """
        if not self.protected and self.has_flag(name):
            self.__flags__[name] = flags
            return True
        # import pdb; pdb.set_trace()  # breakpoint 1d9b2b3f //
        raise Exception("invalid flag name referenced")


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
            raise KeyError("node rights are locked")
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
        if DEBUG is 1:
            print("name exists '%s' = %s" % (name, name in self.__store__))
        return name in self.__store__

    def __update_parent__(self, instance: object, parent: object) -> None:
        """ @abstract Update the parent of an object
            @param instance [DOMObject] Instance of object to update
            @param parent [DOMObject] Parent instance to point to
        """
        # instance.__flags__.set_flag("parent", 0 | FLAG_READ | FLAG_WRITE)
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
            if DEBUG is 1:
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
        if props is None:
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
        """ @abstract Add property to self
            @param name [str] DOM property name
            @param obj [object] valued object
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
            raise(AssertionError("property '%s' does not exist" % propName))
        assert (self.__flags__.test_bit(propName, FLAG_READ) is True)
        self.__store__[propName] = propValue

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
        self.__update_parent__(instance=_instance, parent=self)
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
            @param name [str] Named contexted to return
            @returns [DOMObject] Node object of child
        """
        if name is None:
            return self
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

    def build_schema(self, schema_map: list = []) -> None:
        """ @abstract Build a property tree from a defined schema and name map.
                This is designed for properties values only.
            @param schema_map [list] List of tuples, defining dict, and child
                name
            @returns [None]

            @example Object Schema and Mapping [dict]
            schema = {
                "<attribute_name>": {
                    "cast": <type>,
                    "default": <value>
                    "values": [<value>, ...]
                    "validate_callback": <callable>
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

                _ctx.add_property(_key, _value)


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
    def __init__(self, parent: DOMObject = None, name: str = ""):
        super(DictGroup, self).__init__(name)

        if parent.__name_exists__(name):
            raise(AssertionError("child '%s' exists at parent." % name))
        self.__flags__.set_flag("parent", 0 | FLAG_READ | FLAG_WRITE)
        self.parent = parent
        self.__flags__.lock("parent")
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

    def attach(self, key: str = None,
               obj: object = None,
               flags: int = 0 | FLAG_READ | FLAG_WRITE) -> None:
        """ @abstract Override of DOMObject.attach
            @param key [str] dict key name
            @param obj [object] callable/referable object
            @param flags [byte] byte mask of flags
            @returns [None]
        """
        assert not self.__flags__.protected
        assert not self.__name_exists__(key)

        if isinstance(obj, DOMObject):
            self.__update_parent__(instance=obj, parent=self)

        self.update({key: obj})
        self.__store__[key] = self.__keystore__[key]
        self.__children__.append(key)
        self.__flags__.set_flag(key, flags)

    def detach(self, key: str) -> None:
        """ @abstract Override of DOMObject.deattach
            @param key [str] dict child object name
            @returns [None]
        """
        assert not self.__flags__.protected
        assert self.__name_exists__(key)
        del self.__store__[key]
        del self.__keystore__[key]
        self.__children__.remove(key)

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

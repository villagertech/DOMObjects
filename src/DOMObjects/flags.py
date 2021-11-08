__author__ = "Rob MacKinnon <rome@villagertech.com>"
__package__ = "DOMObjects"
__name__ = "DOMObjects.flags"
__license__ = "MIT"

DEBUG = 0

FLAG_READ = 2**0
FLAG_WRITE = 2**1
FLAG_NAMESPACE = 2**2
FLAG_RESERVED_8 = 2**3
FLAG_RESERVED_16 = 2**4
FLAG_RESERVED_32 = 2**5
FLAG_RESERVED_64 = 2**6
FLAG_RESERVED_128 = 2**7


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

        # --- Expensive Debugging Code Begin ---
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
        # --- Expensive Debugging Code End ---
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
        #   Therefore we immediately default to READONLY to be secure.
        if byteVal == -1:
            return 0 | FLAG_READ

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
            @param name [str] Flag name
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
        _value = self.__setbit__(self.__flags__[name],
                                               FLAG_WRITE, 0)
        self.update_flag(name, _value)

    def unlock(self, name: str = "self") -> None:
        """ @abstract Set the writeable flag to readonly
            @param name [str] Flag name
            @returns [None]
        """
        if not self.has_flag(name):
            raise KeyError("invalid flag name referenced")
        _value = self.__setbit__(self.__flags__[name],
                                               FLAG_WRITE, 1)
        self.update_flag(name, _value)

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

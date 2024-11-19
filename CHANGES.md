* v0.1.0   - Release from beta
            Fix: Set defaults for set_method margs and mkwargs
            Fix: Defined named expansion of keywords for set_method for
                non-existent prop, and set flags on existing method when
                updating.
            Fix: Return default flags where flags are unset.

* v0.1.0b8 - Addition of flag setting on properties, to allow for creation
             of R/O objects.

* v0.1.0b7 - Bug fix for set_namespace and flags.update_flag
             Fix for set_method, missing args
             DOMSchema.path: Feature addition of prop for context path handling

* v0.1.0b4 - Addition of dynamic properties
            DOMObject.new_method: Addition of dynamic properties
            DOMObject.set_method: Addition of dynamic properties

* v0.1.0b3 - Project renamed to DOMObjects
            Project: renamed to avoid contflicting project name
            DictGroup: Key name management bug corrected
            Pypi: pyproject.toml added, and general project directory restructure.

* v0.1.0b2 - Additional features
            DOMSchema.keys: Returns all top-level keys

* v0.1.0b1 - Addition of features
            DOMSchema: Class object for large data structure
            DOMObject.build_schema: Finalized building of schema objects
        Major Updates
            Re-factored DOMFlag->PyDOM.flags.DOMFlags
        Updates
            Updated documentation in PyDOM.flags
        Fixes
            DictGroup.__init__: assignment of parent triggered "flag locked" error
            Misc minor bug fixes

* v0.1.0b - Addition of features
            DOMObject.new_dictgroup: Dict object child type
            DOMObject.del_property: Added reflexive removal of a property
            DOMFlags.del_flag: Added reflexive removal of object flag
            DictGroup: Addition of new class for DictGroup child types
        Renaming of features
            DOMObject.add_property to new_property to match child feature
            DOMObject.add_property_bulk to new_property_bulk to match child feature
        Updated method documentation, and checked Python 3.x code style
        Updated README.md

* v0.0.5 - Updated documentation
        Updated code to Python 3.x style defintions

* v0.0.4 - Addition of features
            DOMObject.json: Object JSON output
            DOMObject.dict: Object dict output
        Documentation cleaning and update of README.md

* v0.0.3 - Addition of features
            DOMObject.path
            DOMObject.new_namespace
            DOMFlags.test_bit
            FLAG_NAMESPACE bitmask added
        Documentation updated

* v0.0.2 - Addition of features
            DOMObject.new_child_bulk
            DOMObject.get_context

* v0.0.1 - First release

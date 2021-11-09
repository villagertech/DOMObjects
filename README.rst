=====================
**DOMObjects v0.1.0**
=====================
---------------------
**About**
---------------------
DOMObjects is designed to create flexible data structures that allows users to
easily traverse to siblings or parents. The datastructure modeled should be
some what familiar compared to the Javascript DOM object structure.

---------------------
**Features**
---------------------
- Scoped namespaces
- Traversable data tree
- Easier data management

Scoped Namespacing
----------------------
Individual namespaces are created to allow for compartmentalized and scoped
configuration and storage allowing for top-down tree transveral and blocking
scope escaping from child objects. Namespace objects also do not require valid
naming conventions, and can contain invalid characters. These objects are
referenced via the `get_context` method.

Traversable Data Tree
-------------------------
Traversing the object tree is simple and similar to the Javascript DOM object
tree. This is by design, by referencing `siblings`, `parent`, or `children`
properties, you can get and manage all aspects of an object.

Easier Data Management
-----------------------
Assignment of callback methods can be done so programatically. The defined
"value" of the property is not limited to static value, but supports dynamic
evaluation. Therefore, with the usage of the ``add_property`` method static
objects (e.g. ``str``, ``int``, ``bool``, etc.), ``callable`` objects, callable object
output, and evaluateable callable objects can be attached to the object tree.

::
     
     def callableDef(var): 
          # Do something with var
          return var
          
     # Assignement of a callback method
     ROOT.add_property("callback", callableDef)
     
     # Referencing the method
     print(ROOT.callback("variable"))
     
     # Define a method as though it were using the @property decorator
     ROOT.add_property("preDefProp", callableDef("use-this-everytime"))
     print(ROOT.preDefProp)
     
--------------------
Getting Started
--------------------
Import ``DOMObjects`` and create a root object. Root objects consist of the top level
namespace object and are the base structure to build your datastructure on.

::
     
     import DOMobjects
     ROOT = DOMobjects.DOMRootObject()
     
Children
---------------------
Out of the box, a root object comes empty, plain and boring. Start by adding
some children by using the ``new_child`` method. Once created it can be
referenced and operated on. Children can also be referenced by context, as
seen further in this example.

::
     
     ROOT.new_child("first_born")
     ROOT.first_born.name
     >>> "first_born"
     child_context = ROOT.first_born.get_context()
     child_context.name
     >>> "first_born"
     
Referencing children by context is the preferred method of operation. As
python does more interesting (and some ways less predictable) operations with
value reference vs call reference, you can save some headache and use context.

Parenting
---------------------

As with creation of any child, there is a parent. This value is automatically
set on the child to match the parent object. This value is also automatically
soft-locked.  While possible to update with private methods, doing so is not
recommended.

::
     
     ROOT.first_born.parent
     >>> "root"
     

Bulk Children
---------------------
Creating one child is great, but lets create more with a single method. Using
the `add_child_bulk` method allows you to pass a `list` of children and create
them automatically.

::

     more_children = ["second_born", "third_born", "forth_born", "fifth_born"]
     ROOT.new_child_bulk(more_children)
     ROOT.children
     >>> ["first_born", "second_born", "third_born", "forth_born", "fifth_born"]
     

Siblings
---------------------
Each child has the ``siblings`` attribute will report all the child nodes
with the same parent.

::

     ROOT.first_born.siblings
     >>> ["second_born", "third_born", "forth_born", "fifth_born"]
     

Namespaces
---------------------
From a parent object calling the ``new_namespace()`` method will create a child
with the `FLAG_NAMESPACE` bit flag set. This flag manages the ability of
children to perform path traversal upward and limits them to within their own namespace.
Namespaces names do not have to conform to standard Python object name limitations.
To operate on this child type, use the `get_context` method on the parent object to retrieve it.

::

     ROOT.new_namespace("new_namespace_object")
     ROOT.new_namespace("{b52702e0-1513-4201-82df-592c05ee7a02}")
     context1 = ROOT.get_context("new_namespace_object")
     context2 = ROOT.get_context("{b52702e0-1513-4201-82df-592c05ee7a02}")
     context1.parent
     >>> None
     

DictGroups
---------------------
Children grouping can be acheived with the usage of the ``new_dictgroup`` method.
The ``DictGroup`` class includes several overrides as an extension to the
``DOMObject`` class.  This allows for ``dict``-like usage and standard property
setting. New children added under this object type group together in a more
user friendly iterable group.

::

     ROOT.new_dictgroup("group")
     ROOT.group.new_child_bulk(["A", "B", "C"])
     ROOT.group["A"].name
     >>> A
     ROOT.group["A"].siblings
     >>> ["B", "C"]
     
Properties
---------------------
Property management for a child generally should not be expensive. Adding,
removing, setting, and getting can be easily achieved with the built-in methods
``new_method``, ``new_property``, ``del_property``, ``set_property``, ``set_method``, and
``get_property``. Properties have the special feature of referencing any kind of
object type. They can be static or dynamic values. Like namespacing, the naming
convention does not have to follow Python object name limitation. In the
following example, both static and dynamic value types can be found.

::

     def demo_def(value):
          return 1+value
     
     ROOT.new_property("value", 1)
     ROOT.value
     >>> 1
     ROOT.new_property("dynamic_call", demo_def)
     ROOT.dynamic_call(1)
     >>> 2
     ROOT.new_property("dynamic_value", demo_def(3))
     ROOT.dynamic_value
     >>> 4
     ROOT.new_method("method", demo_def, [3])
     ROOT.method()
     >>> 3
     demo_list = [1, 2, 3]
     ROOT.new_method("sum", sum, [demo_list])
     ROOT.sum()
     >>> 6
     demo_list = [4, 5, 6]
     ROOT.sum()
     >>> 15
     
Bulk Properties
---------------------
With large systems come large selections of properties. Using the
``new_property_bulk`` method allows for creation of reusable property sets.
If no value is defined (as with the first property in our example), a default
value of ``None`` is assigned.

::

    props = [
        "single_prop",
        ("another_prop", "with_value")
    ]
    ROOT.new_property_bulk(props)
    ROOT.single_prop
    >>> None
    ROOT.another_prop
    >>> "with_value"


--------------------------------------------------------
Building Large Datastructures `(new as of v0.1.0 beta1)`
--------------------------------------------------------
Bootstrapping properties for datastructures with ``DOMObjects`` is made easier by using
the DOMObject's ``build_schema`` method and ``DOMSchema`` objects. Start by creating an schema object, and giving it some structure.

::

    schema = DOMSchema()
    schema.children = {
        "child_1": {
        	"props": {
			    "A": {
				"cast": int,
				"default": 1
			    },
			    "B": {
				"cast": str,
				"default": "string value for child 1"
			    }
		}
        },
        "child_2": {
        	"props": {
        		"A": {
        			"cast": int,
        			"default": 2
        		}
        	},
        	"children": {
			"subchild_1": {},
			"subchild_2": {},
			"subchild_3": {}
        	}
        },
    }
    schema.dictgroups = {
    	"group_1": {}
    	"group_2": {
    		"children": {
			"subchild_1": {
				"props": {
					"A": {
						"cast": int,
						"default": 3
					}
				}
			},
			"subchild_2": {},
			"subchild_3": {}
    		}
	}
    }

Next generate the above schema. To do so, call the ``build_schema`` method on the required context. In this example, we'll use the root object.

::

    ROOT.build_schema(schema)
    ROOT.child_1.A
    >>> 1
    ROOT.child_2.A
    >>> 2
    ROOT.group_2.children
    >>> ["subchild_1","subchild_2","subchild_3"]
    ROOT.group_2["subchild_1"].A
    >>> 3

----------------------------
Attribute and Property Flags
----------------------------

Bit Flags
----------------------------
Properties and children have assigned control flags set allowing for
soft locking. Bit values are found under the ``__flags__`` sub-object.
Directly managing them is not suggested, instead use the built-in methods
``set_flag``, ``get_flag``, ``update_flag``, or ``test_flag`` to update, set, unset, or test value masks.

Valid mask values are available as: ``FLAG_READ``, ``FLAG_WRITE``, or ``FLAG_NAMESPACE``.

Mapping
----------------------------

::

     Bit Position:
     0 1 2 3 4 5 6 7   Flags:
      .--------------- [1] Readeable = FLAG_READ
     /  .------------- [2] Writeable = FLAG_WRITE
     | /  .----------- [4] Namespace = FLAG_NAMESPACE
     | | /  .--------- [8] Reserved
     | | | /  .------- [16] Reserved
     | | | | /  .----- [32] Reserved
     | | | | | /  .--- [64] Reserved
     | | | | | | /  .- [128] Reserved
     | | | | | | | /
     1 1 1 1 1 1 1 1
     ^
      ---- MSB
     
----------------------------
Examples
----------------------------
::

    def demo_def():
        return True

    ROOT = DOMRootObject()
    ROOT.new_child("sample_child")
    ROOT.new_child("sample_sibling")
    ROOT.sample_child.new_child("sub_child")

    moreChildren = ["bulkChild", "anotherChild"]
    ROOT.new_child_bulk(moreChildren)


    # Define a callable property
    ROOT.sample_child.add_method("callable", demo_def)
    print("This prop is callable and %s" % ROOT.sample_child.callable())

    # Define values
    ROOT.sample_child.add_property("value_int", 1)
    ROOT.sample_child.add_property("value_float", 1.00001)

    # Define evaluatable properties like lambdas
    ROOT.sample_child.add_property("bool_eval", (demo_def() !=  True))
    ROOT.sample_child.add_property("child_count", len(ROOT.children))

    ROOT.children              ## returns ["sample_child", "sample_sibling"]
    ROOT.sample_child.sibings  ## returns ["sample_sibling"]

    # Get a node context directly
    sub_child = ROOT.sample_child.sub_child.get_context()
    # or get a node's context via it's parent
    sub_child = ROOT.sample_child.get_context("sub_child")

    # Try getting a Node's object path
    print(sub_child.path)

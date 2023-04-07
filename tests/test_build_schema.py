import DOMObjects

rootDom = DOMObjects.DOMRootObject()

schema = DOMObjects.schema.DOMSchema()
schema.children = {
    "settings": {
        "children": {
            "app": {
                "props": {
                    "lang_locale": {
                        "cast": str,
                        "default": "en_US.UTF-8"
                    },
                    "lang_encoding": {
                        "cast": str,
                        "default": "en_US"
                    }
                }
            }
        },
        "dictgroups": {
            "device": {}
        }
    }
}
schema.dictgroups = {
    "controls": {},
    "devices": {},
    "sessions": {},
    "states": {},
    "history": {},
    "event_log": {}
}

subschema = DOMObjects.schema.DOMSchema(path="controls")
subschema.children = {
    "objects": {
        "props": {
            "value": {"cast": int}
        }
    }
}

# import pdb; pdb.set_trace()  # breakpoint 58de246a //
rootDom.build_schema(schema)
rootDom.build_schema(subschema)

print(rootDom.children)
print(rootDom.controls.children)
print(rootDom.settings.children)
print(rootDom.settings.app.props)

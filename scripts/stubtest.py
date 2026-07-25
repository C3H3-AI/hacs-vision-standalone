import sys, types, importlib.abc, importlib.util

ROOT = "D:/ai-hub/integrations/hacs-vision-standalone"
sys.path.insert(0, ROOT)

STUB_ROOTS = {
    "homeassistant", "aiogithubapi", "aiohttp", "voluptuous",
    "awesomeversion", "packaging", "dompurify", "lit",
}

# Provide a few real symbols that must behave like objects (not just names)
KNOWN = {
    ("homeassistant", "const", "__version__"): "2025.3.0",
}


class _Meta(type):
    """Metaclass so class-level attribute access / subscript also yields _Stub."""
    def __getattr__(cls, name):
        return _Stub
    def __class_getitem__(cls, item):
        return _Stub


class _Stub(metaclass=_Meta):
    """Recursive stub: attribute access, subscript, call all return _Stub.

    A class, so it is usable both as a base class and as a value.
    """
    def __getattr__(self, name):
        return _Stub
    def __init__(self, *a, **k):
        pass
    def __call__(self, *a, **k):
        return _Stub
    def __getitem__(self, k):
        return _Stub
    def __class_getitem__(cls, item):
        return _Stub


class StubLoader(importlib.abc.Loader):
    def __init__(self, fullname):
        self.fullname = fullname
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        module.__getattr__ = lambda name: _Stub
        if self.fullname == "homeassistant.const":
            module.__version__ = "2025.3.0"
            module.Platform = _Stub
        if self.fullname == "homeassistant":
            module.__version__ = "2025.3.0"
        module.__path__ = []  # treat as package


class StubFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        top = fullname.split(".")[0]
        if top in STUB_ROOTS:
            return importlib.util.spec_from_loader(fullname, StubLoader(fullname))
        return None


sys.meta_path.insert(0, StubFinder())

try:
    import custom_components.hacs.vision as v
    print("IMPORT vision OK; async_setup_vision:", hasattr(v, "async_setup_vision"),
          "async_unload_vision:", hasattr(v, "async_unload_vision"))
    from custom_components.hacs.vision import api, hacs_operator, backup, auto_update
    from custom_components.hacs.vision import dependency_checker, entity_ref_finder, hacs_history, hacs_data, response
    from custom_components.hacs.vision.api_mixins import github_auth, github_actions, hacs_ops, readme_translate
    print("IMPORT all vision submodules OK")
    import custom_components.hacs as h
    print("IMPORT hacs main OK; async_setup_entry:", hasattr(h, "async_setup_entry"))
    print("ALL_IMPORTS_OK")
except Exception:
    import traceback
    traceback.print_exc()
    print("IMPORT_FAILED")

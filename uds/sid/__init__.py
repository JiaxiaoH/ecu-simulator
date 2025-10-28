#__init__.py
import os
import pkgutil
import importlib

# scan and import all SID_0xXX.py files
SID_DIR = os.path.dirname(__file__)

for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{module_name}")
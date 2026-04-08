"""
SHIM - DataAccess re-exported from the split package.
This file is kept for backwards compatibility with any direct imports.
Import from core.data_access or core.data_access._queries instead.
"""
import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from core.data_access._queries import DataAccess  # noqa: F401, E402

__all__ = ["DataAccess"]

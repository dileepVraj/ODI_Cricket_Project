# This file has been superseded by the core/data_access/ package.
# Python resolves `core.data_access` to the package directory.
# All imports (e.g. `from core.data_access import DataAccess`) continue to work unchanged.
from core.data_access._dal import DataAccess

__all__ = ["DataAccess"]

"""Get trending homebrew."""
from importlib.metadata import PackageNotFoundError, version
try:
    __version__ = version('trending-homebrew')
except PackageNotFoundError:
    __version__ = '0.1.0'

del PackageNotFoundError
del version

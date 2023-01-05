from importlib.metadata import PackageNotFoundError, version
try:
    __version__ = version('trending-homebrew')
except PackageNotFoundError:
    __version__ = '0.1.0'
try:
    from ._trending_homebrew import longest  # noqa
except ImportError:
    def longest(args):
        return max(args, key=len)

del PackageNotFoundError
del version

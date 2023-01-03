__version__ = '0.1.0'
try:
    from ._trending_homebrew import longest  # noqa
except ImportError:
    def longest(args):
        return max(args, key=len)

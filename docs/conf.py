# -*- coding: utf-8 -*-
import os
import traceback

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
source_suffix = '.rst'
master_doc = 'index'
project = 'trending_homebrew'
year = '2023'
author = 'John Patrick Roach'
copyright = '{0}, {1}'.format(year, author)
try:
    from pkg_resources import get_distribution

    version = release = get_distribution('trending_homebrew').version
except Exception:
    traceback.print_exc()
    version = release = '0.1.0'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'trac'
todo_include_todos = False
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/johnpatrickroach/trending-homebrew/issues/%s', '#'),
    'pr': ('https://github.com/johnpatrickroach/trending-homebrew/pull/%s', 'PR #'),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
htmlhelp_basename = 'trending_homebrewdoc'
html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
    '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)
latex_documents = [
    (master_doc, 'trending_homebrew.tex',
     'trending-homebrew Documentation',
     'John Patrick Roach', 'manual'),
]
man_pages = [
    (master_doc, 'trending_homebrew',
     'trending-homebrew Documentation',
     [author], 1)
]
texinfo_documents = [
    (master_doc, 'trending_homebrew',
     'trending-homebrew Documentation',
     author,
     'trending_homebrew',
     'One line description of project.',
     'Miscellaneous'),
]
napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False

import os
import types
from glob import glob
from importlib import import_module
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader


BASEDIR = Path(__file__).resolve().parent
JINJAENV = Environment(loader=FileSystemLoader(BASEDIR / '_templates'))

SITEMAP_BASE = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{}
</urlset>'''
SITEMAP_URL = '''
  <url>
    <loc>{url}</loc>
    <changefreq>monthly</changefreq>
    <priority>{priority}</priority>
  </url>'''


def markdown_to_html_filter(md):
    res = markdown.markdown(md, extensions=['footnotes'])
    res = res.replace('<h1>', '<h1 class="mt-5 mb-4">')
    res = res.replace('<h2>', '<h2 class="mt-4 mb-3">')
    res = res.replace('<h3>', '<h3 class="mt-4 mb-3">')
    res = res.replace('<img ', '<img width="100%" ')
    res = res.replace('<blockquote>', '<blockquote class="blockquote ps-3" style="border-left: solid;">')
    return res

JINJAENV.filters['markdown'] = markdown_to_html_filter


def getattr_filter(obj, attr):
    return getattr(obj, attr, None)

JINJAENV.filters['getattr'] = getattr_filter


def getattr_list_filter(obj, attrs):
    return [getattr(obj, attr, None) for attr in attrs]

JINJAENV.filters['getattrs'] = getattr_list_filter


def format_link(link, parenting):
    """
    Add parenting if needed, so links work on both local and deployed env
    """
    if link[0] == '/':
        return f'{parenting}{link}'
    return link

JINJAENV.filters['link'] = format_link


def import_path(path):
    """
    Import py file path from '_data' dir as a module
    """
    if path.endswith('.py'):
        path = path[:-3]
    path = path.replace('/', '.')

    module = import_module('_data.' + path)
    module.__name__ = path

    return module


def get_vars(module):
    """
    Return variables of the passed module
    """
    return {k: v for k, v in vars(module).items() if not k.startswith('_')}


def make_xml_url(lang, tmpl_path, data_node, data_tree):
    """
    Generate an xml piece with the url for sitemap
    """
    url = f'{data_tree.base_url}/{lang}/{tmpl_path}'
    priority = getattr(data_node, 'priority', None) or "1.0"
    return SITEMAP_URL.format(url=url, priority=priority)


def tree_add(root, module):
    """
    Add module to the root according to its path containing in module.__name__
    """
    prev = root

    for part in module.__name__.split('.'):
        if part == '__init__':  # special case: skip applying __init__
            break               # to later apply its vars on prev module
        part_module = getattr(prev, part, types.ModuleType(part))
        setattr(prev, part, part_module)
        prev = part_module

    [setattr(part_module, k, v) for k, v in get_vars(module).items()]


def read_tmpl_pathes():
    """
    Find all the html templates visible to end user
    (not starting with _) in '_templates' dir
    """
    os.chdir(BASEDIR / '_templates')

    pathes = []
    for path in glob('**/*.html', recursive=True):
        if not path.startswith('_') and path.split('/')[-1][0].isalpha():
            pathes.append(path)

    return pathes


def read_data_tree():
    """
    Import all the py files from '_data' dir into a tree module structure
    """
    os.chdir(BASEDIR / '_data')

    try:
        root = import_path('__init__.py')
    except ModuleNotFoundError:
        root = types.ModuleType('__init__')

    pathes = glob('**/*.py', recursive=True)
    try:
        del pathes[pathes.index('__init__.py')]
    except ValueError:
        pass

    for path in pathes:
        module = import_path(path)
        tree_add(root, module)

    return root


def get_langs_data(data_tree):
    """
    Extract lang modules to dict, to iterate over them
    """
    os.chdir(BASEDIR / '_data')
    res = {}

    for item in glob('*'):
        if not item.startswith('_') and os.path.isdir(item):
            res[item] = getattr(data_tree, item)

    return res


def find_data_node(lang, tmpl_path, data_tree):
    """
    Find a node in data tree according to language and template path provided
    """
    node = getattr(data_tree, lang, None)

    for part in tmpl_path[:-5].split('/'):
        if node:
            node = getattr(node, part, None)

    return node


def render(tmpl_path, lang, data_node, langs_dict, data_tree):
    kwargs = {
        'DATA': data_tree,
        'LANG': langs_dict[lang],
        'LANG_DIR': lang,
        'LANGS': langs_dict,
        'PARENTING': '/'.join(['..'] * (tmpl_path.count('/') + 1)),
        **get_vars(data_node),
    }
    html = JINJAENV.get_template(tmpl_path).render(**kwargs)

    path = Path(BASEDIR / lang / tmpl_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)


def main():
    xml_urls = []
    data_tree = read_data_tree()
    langs_dict = get_langs_data(data_tree)

    for tmpl_path in read_tmpl_pathes():
        for lang in langs_dict:
            if data_node := find_data_node(lang, tmpl_path, data_tree):
                print('Render:', lang, tmpl_path)
                render(tmpl_path, lang, data_node, langs_dict, data_tree)
                xml_urls.append(make_xml_url(lang, tmpl_path, data_node, data_tree))
            else:
                print("  Didn't render (no matching .py file found):", lang, tmpl_path)

    print(f'\nGenerate sitemap.xml: {len(xml_urls)} URLs')
    Path(BASEDIR / 'sitemap.xml').write_text(SITEMAP_BASE.format(''.join(xml_urls)))


if __name__ == '__main__':
    main()

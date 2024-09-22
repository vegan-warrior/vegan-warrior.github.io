import shutil
from pathlib import Path
from importlib import import_module

from jinja2 import Environment, FileSystemLoader

import config as CFG


BASEDIR = Path(__file__).resolve().parent
JINJAENV = Environment(loader=FileSystemLoader(BASEDIR / 'templates'))

SITEMAP_BASE_TMPL = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{}
</urlset>'''
SITEMAP_URL_TMPL = '''
  <url>
    <loc>{url}</loc>
    <changefreq>monthly</changefreq>
    <priority>{priority}</priority>
  </url>'''


def get_vars(module):
    """
    Return variables of the passed module
    """
    return {k: v for k, v in vars(module).items() if not k.startswith('_')}


def _make_xml_url(url, priority):
    """
    Sitemaps generation help function
    """
    url = 'https://vegan-warrior.github.io' + url
    xml_url = SITEMAP_URL_TMPL.format(url=url, priority=priority)
    return xml_url


def make_sitemap():
    """
    Find all the URLs in lang navbars and generate sitemap.xml from them
    """
    xml_urls = []

    for lang in CFG.languages:
        xml_urls.append(_make_xml_url(f'/{lang}', '1.0'))

        base = import_module(f'{lang}.base')
        for item in base.navbar_items[1:]:
            xml_urls.append(_make_xml_url(item['link'], '0.9'))

    sitemap = SITEMAP_BASE_TMPL.format(''.join(xml_urls))

    with open('sitemap.xml', 'w') as f:
        f.write(sitemap)

    print(f'sitemap.xml generated: {len(xml_urls)} URLs')


def render(lang, page, base):
    """
    Render one page
    """
    template = JINJAENV.get_template(f'{page}.html')
    kwargs = get_vars(base)

    try:
        module = import_module(f'{lang}.{page}')
        kwargs = {**kwargs, **get_vars(module)}
    except ModuleNotFoundError as exc:
        print('    ', exc)

    return template.render(**kwargs)


def render_pages():
    """
    Find and render all the pages
    """
    for lang in CFG.languages:
        dirpath = BASEDIR / lang
        dirpath.mkdir(parents=True, exist_ok=True)

        for page in CFG.pages:
            print('Render', lang, page)
            base = import_module(f'{lang}.base')
            with open(dirpath / f'{page}.html', 'w') as f:
                f.write(render(lang, page, base))


if __name__ == '__main__':
    render_pages()
    make_sitemap()

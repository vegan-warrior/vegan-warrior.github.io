import glob
import shutil
from pathlib import Path
from importlib import import_module

import markdown
from jinja2 import Environment, FileSystemLoader

import config as CFG


def markdown_to_html(md):
    res = markdown.markdown(md, extensions=['footnotes'])
    res = res.replace('<h1>', '<h1 class="mt-5 mb-4">')
    res = res.replace('<h2>', '<h2 class="mt-4 mb-3">')
    res = res.replace('<h3>', '<h3 class="mt-4 mb-3">')
    res = res.replace('<img ', '<img width="100%" ')
    res = res.replace('<blockquote>', '<blockquote class="blockquote ps-3" style="border-left: solid;">')
    return res


BASEDIR = Path(__file__).resolve().parent
JINJAENV = Environment(loader=FileSystemLoader(BASEDIR / 'templates'))
JINJAENV.filters['markdown'] = markdown_to_html

SITEMAP_BASE_TMPL = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{}
</urlset>'''
SITEMAP_URL_TMPL = '''
  <url>
    <loc>{url}</loc>
    <changefreq>monthly</changefreq>
    <priority>{priority}</priority>
  </url>'''


def import_path(path):
    if path.endswith('.py'):
        path = path[:-3]
    return import_module(path.replace('/', '.'))


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
    Generate sitemap.xml for each page
    """
    xml_urls = []

    for lang in CFG.languages:
        xml_urls.append(_make_xml_url(f'/{lang}', '1.0'))
        for page in CFG.pages:
            if page != 'index':
                xml_urls.append(_make_xml_url(f'/{lang}/{page}.html', '0.9'))

    sitemap = SITEMAP_BASE_TMPL.format(''.join(xml_urls))
    Path(BASEDIR / 'sitemap.xml').write_text(sitemap)
    print(f'sitemap.xml generated: {len(xml_urls)} URLs')


def read_kwargs(lang, page, pagecfg=None):
    """
    Read all the kwargs needed to render the page
    """
    base = import_path(f'{lang}/base')
    kwargs = get_vars(base)
    pagecfg = pagecfg or {}

    try:
        module = import_path(f'{lang}/{page}')
        kwargs = {**kwargs, **get_vars(module)}
    except ModuleNotFoundError as exc:
        print('    ', exc)

    # if import_dirmodules enabled, import neighbour modules under 'dirmodules' name
    if pagecfg.get('import_dirmodules'):
        dirmodules = {}
        for path in sorted(glob.glob(lang + '/' + '/'.join(page.split('/')[:-1]) + '/*.py')):
            if path != f'{lang}/{page}.py':
                dirmodules[path[:-3].split('/')[-1]] = import_path(path)
        kwargs['dirmodules'] = dirmodules

    # if read_other_modules_kwargs enabled, import specified modules under the specified names
    if others := pagecfg.get('read_other_modules_kwargs'):
        for other_name, other_path in others.items():
            kwargs[other_name] = read_kwargs(lang, other_path, pagecfg=CFG.pages[other_path])

    return kwargs


def render(page, kwargs):
    template = JINJAENV.get_template(f'{page}.html')
    return template.render(**kwargs)


def render_pages():
    """
    Find and render all the pages
    """
    for lang in CFG.languages:
        dirpath = BASEDIR / lang
        dirpath.mkdir(parents=True, exist_ok=True)

        for page, pagecfg in CFG.pages.items():
            path = Path(dirpath / f'{page}.html')
            path.parent.mkdir(parents=True, exist_ok=True)
            kwargs = read_kwargs(lang, page, pagecfg=pagecfg)

            print('Render', lang, page)
            path.write_text(render(page, kwargs))


if __name__ == '__main__':
    render_pages()
    make_sitemap()

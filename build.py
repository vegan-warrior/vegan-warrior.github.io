import shutil
from pathlib import Path
from importlib import import_module

from jinja2 import Environment, FileSystemLoader

import config as CFG


BASEDIR = Path(__file__).resolve().parent
JINJAENV = Environment(loader=FileSystemLoader(BASEDIR / 'templates'))


def get_vars(module):
    return {k: v for k, v in vars(module).items() if not k.startswith('_')}


def render(lang, page, base):
    template = JINJAENV.get_template(f'{page}.html')
    kwargs = get_vars(base)

    try:
        module = import_module(f'{lang}.{page}')
        kwargs = {**kwargs, **get_vars(module)}
    except ModuleNotFoundError as exc:
        print('    ', exc)

    return template.render(**kwargs)


def main():
    for lang in CFG.languages:
        dirpath = BASEDIR / lang
        dirpath.mkdir(parents=True, exist_ok=True)

        for page in CFG.pages:
            print('Render', lang, page)
            base = import_module(f'{lang}.base')
            with open(dirpath / f'{page}.html', 'w') as f:
                f.write(render(lang, page, base))


if __name__ == '__main__':
    main()

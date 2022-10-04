import hashlib
import os
from collections import OrderedDict

from bs4 import BeautifulSoup
from jinja2.ext import Extension
from jinja2.nodes import CallBlock
from jinja2.parser import Parser
from jinja2.runtime import Macro

from flask_pack.config import Config
from flask_pack.exceptions import FileTypeUnsupported
from flask_pack.line import Line
from flask_pack.utils import get_env_vars


class FlaskPackExtension(Extension):
    tags = {'pack'}

    def __init__(self, *args, **kwargs) -> None:
        super(FlaskPackExtension, self).__init__(*args, **kwargs)
        self.config = Config()

    def parse(self, parser: Parser) -> CallBlock:
        env_vars = get_env_vars(self.environment)
        self.config.update(**env_vars)

        lineno = next(parser.stream).lineno
        args = [parser.parse_expression()]
        body = parser.parse_statements(['name:endpack'], drop_needle=True)

        callblock = CallBlock(self.call_method('pack', args), [], [], body)
        callblock.set_lineno(lineno)
        return callblock

    def pack(self, extension: str, caller: Macro) -> str:
        extension = extension.lower()
        html = caller()
        html_hash = self.make_hash(html)

        if not os.path.exists(self.config.pack_output_dir):
            os.makedirs(self.config.pack_output_dir)

        cache_path = os.path.join(self.config.pack_output_dir, f'{html_hash}.{extension}')
        if os.path.exists(cache_path):
            filename = os.path.join(self.config.pack_output_url, os.path.basename(cache_path), )
            return self.render_element(filename, extension)

        assets = OrderedDict()
        soup = BeautifulSoup(html, 'html.parser')
        for line in self.find_lines(soup):

            if line.url:
                tag_path = self.config.pack_find_static(line.url)
                text = open(tag_path, 'r', encoding='utf-8')
            else:
                text = line.string

            try:
                packer = self.config.pack_packers[line.mimetype]
            except KeyError:
                raise FileTypeUnsupported

            if os.path.exists(cache_path):
                assets[cache_path] = None
                continue
            else:
                packed = packer.compile(text.read())
                assets[cache_path] = "\n" + packed

        blocks = ''
        for cache_path, asset in assets.items():
            if not os.path.exists(cache_path):
                with open(cache_path, 'w', encoding='utf-8') as file:
                    file.write(asset)
            filename = os.path.join(self.config.pack_output_url, os.path.basename(cache_path))
            blocks += self.render_element(filename, extension)

        return blocks

    def make_hash(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        html_hash = hashlib.md5(html.encode('utf-8'))

        for line in self.find_lines(soup):
            if line.url:
                line_path = self.config.pack_find_static(line.url)
                with open(line_path, 'r', encoding='utf-8') as f:
                    while True:
                        content = f.read(1024)
                        if content:
                            html_hash.update(content.encode('utf-8'))
                        else:
                            break

        return html_hash.hexdigest()

    @staticmethod
    def find_lines(soup: BeautifulSoup) -> Line:
        tags = ['link', 'style', 'script']
        for tag in soup.find_all(tags):
            line = Line()
            line.string = tag.string

            url = tag.get('src') or tag.get('href')
            if url and (url.startswith('http') or url.startswith('//')):
                continue
            line.url = url

            match tag.name:
                case 'style' | 'link':
                    line.mimetype = 'text/css'
                case 'script':
                    line.mimetype = 'text/javascript'
                case _:
                    raise FileTypeUnsupported

            yield line

    @staticmethod
    def render_element(filename: str, type_: str) -> str:
        match type_.lower():
            case 'css':
                return f'<link type="text/css" rel="stylesheet" href="{filename}">'
            case 'js':
                return f'<script type="text/javascript" src="{filename}"></script>'
            case _:
                raise FileTypeUnsupported

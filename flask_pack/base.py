import os

from flask import Flask

from flask_pack.exceptions import StaticNotInitialized
from flask_pack.packers.css import CssPacker
from flask_pack.packers.javascript import JavaScriptPacker
from flask_pack.utils import get_find_static


class FlaskPack:

    def __init__(self, app: Flask = None) -> None:
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        app.jinja_env.add_extension('flask_pack.FlaskPackExtension')
        app.jinja_env.pack_output_dir = os.path.join(app.static_folder, 'sdist')
        app.jinja_env.pack_output_url = os.path.join(app.static_url_path, 'sdist')
        app.jinja_env.pack_packers = {'text/css': CssPacker, 'text/javascript': JavaScriptPacker}
        app.jinja_env.pack_find_static = get_find_static(app)
        self.app = app

    def set_packer(self, mimetype: str, packer: any) -> None:
        if not hasattr(self, 'app') or self.app is None:
            raise StaticNotInitialized

        self.app.jinja_env.pack_packers[mimetype] = packer

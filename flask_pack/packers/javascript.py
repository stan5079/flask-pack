from rjsmin import jsmin


class JavaScriptPacker(object):

    @classmethod
    def compile(cls, js: str, *args, **kwargs) -> str:
        return jsmin(js)

class Config(dict):

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.update(**kwargs)

    def __getattr__(self, key: str) -> any:
        return self[key]

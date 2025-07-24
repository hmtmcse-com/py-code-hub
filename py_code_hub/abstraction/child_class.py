from py_code_hub.abstraction.base_abc import BaseABC


class ChildClass(BaseABC):

    def unlimited(self, name: str):
        pass

    def implement_it(self, name: str, age: int, **kwargs):
        pass

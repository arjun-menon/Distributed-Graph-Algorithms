import ast


class Label(stmt):
    _fields = ['name', 'body']
    def __init__(self, name, body):
        self.name = name
        self.body = body


class Event(stmt):
    _fields = ['name', 'arg', 'at', 'body']
    def __init__ (self, name, arg, at=None, body):
        self.name = name
        self.arg = arg
        self.at = at
        self.body = body

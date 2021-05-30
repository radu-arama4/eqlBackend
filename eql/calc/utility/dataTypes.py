import weakref


class NonTerminalNode:
    instances = []

    def __init__(self, name):
        self.name = name
        self.nodeList = []
        self.__class__.instances.append(weakref.proxy(self))

    def __str__(self):
        return f"<{self.name}>"


class TerminalNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"{self.name.upper()} " + "\"" + self.value + "\""


class Filter:
    def __init__(self, name, values):
        self.name = name
        self.values = values


class Expression:
    def __init__(self, assigned, terms):
        self.assigned = assigned
        self.terms = terms


class Print:
    def __init__(self, words):
        self.words = words

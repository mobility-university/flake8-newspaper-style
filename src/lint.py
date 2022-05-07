#!/usr/bin/env python3

class FunctionDefinition():
    def __init__(self, name, line, statements=None):
        self.name = name
        self.line = line
        self.statements = statements or []
    
    def __repr__(self):

        return f"function {self.name} ({self.line})\n  {'  '.join(str(a) for a in self.statements)}"

class FunctionCall():
    def __init__(self, name, parameter, line):
        self.name = name
        self.parameter = parameter
        self.line = line

    def __repr__(self):
        return f"call {self.name}({', '.join(str(a) for a in self.parameter)}) ({self.line})"


guten_AST = [
    FunctionDefinition("headline", 1, statements=[FunctionCall("text", [1, 2], 3)]),
    FunctionDefinition("text", 5),
    ]

schlechter_AST = [
    FunctionDefinition("text", 1),
    FunctionDefinition("headline", 5, statements=[FunctionCall("text", [1, 2], 7)]),
    ]


schlechterer_AST = [
    FunctionDefinition("text", 1),
    FunctionDefinition("headline", 5, statements=[
        FunctionDefinition("subheadline", 6, statements=[
             FunctionCall("text", [1, 2], 7)]),]])
    ]


def lint(ast):
    """
    >>> lint(guten_AST)
    ''
    >>> lint(schlechter_AST)
    'file.py(7): violation of newspaper style. Function text() defined in line 1'

    """
    function_by_line = {func.name: func.line for func in ast if isinstance(func, FunctionDefinition)}
    
    for func in ast:
        for statement in func.statements:

            if not isinstance(statement, FunctionCall):
                continue
    
            if statement.line > function_by_line[statement.name]:
                return f'file.py({statement.line}): violation of newspaper style. Function {statement.name}() defined in line {function_by_line[statement.name]}'

    return ""

"""
def headline():
    ...

def text():
    ...

text(1, 2)
"""

for element in guten_AST:
    print(element)
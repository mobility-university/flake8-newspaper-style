import ast
import importlib.metadata

NEWS100 = "NEWS100 newspaper style: function {name} defined in line {line} should be moved down"


class Plugin:

    name: str = __name__
    version: str = importlib.metadata.version(__name__)

    def __init__(self, tree: ast.AST) -> None:
        self.tree = tree

    def run(self):
        """
        >>> def lint(code):
        ...     for line_no, col, msg, _ in Plugin(ast.parse(code)).run():
        ...         print(f"{line_no}:{col} {msg}")
        >>> lint('''
        ... def headline():
        ...     text()
        ... def text():
        ...     ...
        ... ''')
        >>> lint('''
        ... def headline():
        ...     ...
        ... headline()
        ... ''')
        >>> lint('''def text():
        ...     ...
        ... def headline():
        ...     text()
        ... ''')
        4:4 NEWS100 newspaper style: function text defined in line 1 should be moved down
        >>> lint('''class A:
        ...     def text():
        ...         ...
        ...     def headline():
        ...         text()
        ... ''')
        5:8 NEWS100 newspaper style: function text defined in line 2 should be moved down
        >>> lint('''class A:
        ...     def text(self):
        ...         ...
        ...     def headline(self):
        ...         self.text()
        ... ''')
        5:8 NEWS100 newspaper style: function text defined in line 2 should be moved down
        >>> lint('''class A:
        ...     def text(self):
        ...         ...
        ...     def headline(self):
        ...         A.text()
        ... ''')
        5:8 NEWS100 newspaper style: function text defined in line 2 should be moved down
        >>> lint('''class A:
        ...     def text(self):
        ...         def subtext():
        ...             ...
        ...     def headline(self):
        ...         subtext()
        ... ''')
        >>> lint('''class A:
        ...     def text(self):
        ...         def subtext():
        ...             def subsubtext():
        ...                 ...
        ...     def headline(self):
        ...         subsubtext()
        ... ''')
        >>> lint('''class A:
        ...     def text(self):
        ...         ...
        ... class B:
        ...     def headline(self):
        ...         A.text()
        ... ''')
        6:8 NEWS100 newspaper style: function text defined in line 2 should be moved down
        >>> lint('''def text():
        ...     ...
        ... def headline():
        ...     return f'{text()}'
        ... ''')
        4:14 NEWS100 newspaper style: function text defined in line 1 should be moved down
        >>> lint('''def text():
        ...     ...
        ... def headline():
        ...     return lambda: text()
        ... ''')
        4:19 NEWS100 newspaper style: function text defined in line 1 should be moved down
        >>> lint('''def text():
        ...     ...
        ... def headline():
        ...     def sub():
        ...         return f'{text()}'
        ... ''')
        5:18 NEWS100 newspaper style: function text defined in line 1 should be moved down
        >>> lint('''def headline():
        ...     def sub():
        ...         return 'abc'
        ...     sub() # within a function newspaper style cannot be applied
        ... ''')
        >>> lint('''def headline():
        ...     class A:
        ...         def sub(self):
        ...             return 'abc'
        ...         def sub2(self):
        ...             sub()
        ... ''')
        6:12 NEWS100 newspaper style: function sub defined in line 3 should be moved down
        >>> lint('''def text():
        ...     ...
        ... def headline():
        ...     text = '123'
        ... ''')
        >>> lint('''
        ... def headline():
        ...     ...
        ... if __name__ == '__main__':
        ...     headline()
        ... ''')
        >>> lint('''
        ... def headline():
        ...     def a():
        ...         ...
        ...     def b():
        ...         ...
        ...     a()
        ...     b()
        ... ''')
        >>> lint('''
        ... def headline():
        ...     def a():
        ...         ...
        ... def text():
        ...     def a():
        ...         ...
        ...     a()
        ... ''')
        >>> lint('''
        ... def recursive():
        ...     recursive()
        ... ''')
        >>> lint('''
        ... class A:
        ...     def a(self):
        ...         ...
        ... def b():
        ...     A.a()
        ... ''')
        6:4 NEWS100 newspaper style: function a defined in line 3 should be moved down
        """
        visitor = Visitor()
        visitor.visit(self.tree)
        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.functions = []
        self.scope = []
        self.errors = []

    def visit_FunctionDef(self, node):
        self.scope.append(node.name)
        self.functions.append((list(self.scope), node.name, node.lineno))
        self.generic_visit(node)
        self.scope.pop()

    def visit_ClassDef(self, node):
        self.scope.append(f'class {node.name}')
        self.generic_visit(node)
        self.scope.pop()

    def visit_Call(self, node):
        name = None
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            if node.func.value.id in self.determine_class_scopes():
                self.check_function_call(
                    name=node.func.attr,
                    line=node.lineno,
                    col=node.col_offset,
                    class_name=node.func.value.id,
                )
                return
            if node.func.value.id not in ('self', 'super'):
                return
            name = node.func.attr
        self.check_function_call(name=name, line=node.lineno, col=node.col_offset)

    def determine_class_scopes(self):
        scopes = set()
        for scope in self.scope:
            if not scope.startswith('class '):
                continue
            scopes.add(scope[len('class '):])
        for scope, _, _ in self.functions:
            if not scope:
                continue
            if not scope[0].startswith('class '):
                continue
            scopes.add(scope[0][len('class '):])
        return scopes

    def check_function_call(self, name, line, col, class_name=None):
        if not self.scope:
            return None
        matching_function = (
            self.get_matching_function(name)
            if not class_name
            else self.get_matching_class_function(class_name, name)
        )
        if not matching_function:
            return None
        _scope, _name, matching_line = matching_function
        if matching_line < line:
            self.errors.append(
                (line, col, NEWS100.format(name=name, line=matching_line))
            )
        return None

    def get_matching_class_function(self, class_name, name):
        for scope, fname, line in self.functions:
            if not scope:
                continue
            if self.scope and scope[0] == self.scope[0]:
                for lhs, rhs in zip(scope, scope[1:]):
                    if lhs != f'class {class_name}':
                        continue
                    if rhs == name:
                        return (scope, rhs, line)
                continue

            if scope[0] == f'class {class_name}':
                if fname == name:
                    return (scope, fname, line)
        return None

    def get_matching_function(self, name):
        for scope, fname, line in self.functions:
            if scope and self.scope and scope[0] == self.scope[0]:
                for lhs, rhs in zip(scope, scope[1:]):
                    if not lhs.startswith('class '):
                        continue
                    if rhs == name:
                        return (scope, rhs, line)
                continue
            if len(scope) > 1:
                continue
            if name != fname:
                continue
            return (scope, fname, line)

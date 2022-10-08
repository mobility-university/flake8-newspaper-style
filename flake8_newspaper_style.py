import ast
import importlib.metadata

NEW100 = "NEW100 newspaper style: function {name} defined in line {line} should be moved down"


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
        >>> lint('''
        ... unknown_function()
        ... ''')
        >>> lint('''def text():
        ...     ...
        ... def headline():
        ...     text()
        ... ''')
        4:4 NEW100 newspaper style: function text defined in line 1 should be moved down
        >>> lint('''class A:
        ...     def text():
        ...         ...
        ...     def headline():
        ...         text()
        ... ''')
        5:8 NEW100 newspaper style: function text defined in line 2 should be moved down
        >>> lint('''class A:
        ...     def text(self):
        ...         ...
        ...     def headline(self):
        ...         self.text()
        ... ''')
        5:8 NEW100 newspaper style: function text defined in line 2 should be moved down
        >>> lint('''class A:
        ...     def text(self):
        ...         ...
        ...     def headline(self):
        ...         A.text()
        ... ''')
        5:8 NEW100 newspaper style: function text defined in line 2 should be moved down
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
        6:8 NEW100 newspaper style: function text defined in line 2 should be moved down
        >>> lint('''def text():
        ...     ...
        ... def headline():
        ...     return f'{text()}'
        ... ''')
        4:14 NEW100 newspaper style: function text defined in line 1 should be moved down
        >>> lint('''async def text():
        ...     ...
        ... async def headline():
        ...     return f'{text()}'
        ... ''')
        4:14 NEW100 newspaper style: function text defined in line 1 should be moved down
        >>> lint('''async def text():
        ...     ...
        ... async def headline():
        ...     yield from text()
        ... ''')
        4:15 NEW100 newspaper style: function text defined in line 1 should be moved down
        >>> lint('''def text():
        ...     ...
        ... def headline():
        ...     return lambda: text()
        ... ''')
        4:19 NEW100 newspaper style: function text defined in line 1 should be moved down
        >>> lint('''def text():
        ...     ...
        ... def headline():
        ...     def sub():
        ...         return f'{text()}'
        ... ''')
        5:18 NEW100 newspaper style: function text defined in line 1 should be moved down
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
        6:12 NEW100 newspaper style: function sub defined in line 3 should be moved down
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
        6:4 NEW100 newspaper style: function a defined in line 3 should be moved down
        >>> lint('''
        ... def decorator():
        ...     ...
        ... @decorator
        ... def func():
        ...     ...
        ... ''')
        >>> lint('''
        ... def decorator(param):
        ...     ...
        ... @decorator(123)
        ... def func():
        ...     ...
        ... ''')
        >>> lint('''
        ... def special():
        ...     ...
        ... class A:
        ...     a=special()
        ... ''')
        >>> lint('''
        ... class Test:
        ...     counter = 0
        ...     def do_something(self):
        ...         if self.counter < 1:
        ...             self.counter += 1
        ...             self.do_something()
        ... ''')
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

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_FunctionDef(self, node):
        self.scope.append(node)
        self.functions.append((list(self.scope), node))
        if not node.decorator_list:
            self.generic_visit(node)
        self.scope.pop()

    def visit_ClassDef(self, node):
        self.scope.append(node)
        if not any(isinstance(a, (ast.Assign, ast.Expr)) for a in node.body):
            self.generic_visit(node)
        self.scope.pop()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.check_function_call(
                name=node.func.id, line=node.lineno, col=node.col_offset
            )
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

            def is_in_current_scope():
                return node.func.attr in [scope.name for scope in self.scope]

            if not is_in_current_scope():
                self.check_function_call(
                    name=node.func.attr, line=node.lineno, col=node.col_offset
                )

    def determine_class_scopes(self):
        scopes = set()
        for scope in self.scope:
            if not isinstance(scope, ast.ClassDef):
                continue
            scopes.add(scope.name)
        for scope, _ in self.functions:
            if not scope:
                continue
            if not isinstance(scope[0], ast.ClassDef):
                continue
            scopes.add(scope[0].name)
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
        node = matching_function
        if node.lineno < line:
            self.errors.append((line, col, NEW100.format(name=name, line=node.lineno)))
        return None

    def get_matching_class_function(self, class_name, name):
        def matches(lhs, rhs):
            return (
                isinstance(lhs, ast.ClassDef) and lhs.name == class_name and rhs == name
            )

        for scope, node in self.functions:
            if not scope:
                continue
            if scope[0] == self.scope[0]:
                for lhs, rhs in zip(scope, scope[1:]):
                    if matches(lhs, rhs.name):
                        return node
                continue

            if matches(scope[0], node.name):
                return node
        return None

    def get_matching_function(self, name):
        for scope, node in self.functions:
            if scope and scope[0] == self.scope[0]:
                for lhs, rhs in zip(scope, scope[1:]):
                    if isinstance(lhs, ast.ClassDef) and rhs.name == name:
                        return node
                continue
            if len(scope) == 1 and name == node.name:
                return node
        return None

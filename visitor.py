import ast

class Visitor(ast.NodeVisitor):
	def __init__(self):
		self.functions = []

	def visit_FunctionDef(self, node):
		self.functions.append(node)
		self.generic_visit(node)
		
	def visit_AsyncFunctionDef(self, node):
		self.visit_FunctionDef(node)
	
	@staticmethod
	def get_functions(code: str):
		tree = ast.parse(code)
		visi = Visitor()
		visi.visit(tree)
		return [(func.name, ast.unparse(func)) for func in visi.functions]
import ast

class Visitor(ast.NodeVisitor):
	def __init__(self):
		self.names = []
	
	def visit_Name(self, node):
		self.names.append(node)
		self.generic_visit(node)

	@staticmethod
	def get_names(code: str):
		if code is None: return []

		tree = ast.parse(code)
		visi = Visitor()
		visi.visit(tree)

		return [*map(lambda nn: nn.id, visi.names)]
import ast

class Visitor(ast.NodeVisitor):
	def __init__(self):
		self.names = []

	def generic_visit(self, node):
		try:
			self.names.append(node.name)
		except:
			pass
		
		return super().generic_visit(node)

	@staticmethod
	def get_names(code: str):
		if code is None: return []

		tree = ast.parse(code)
		visi = Visitor()
		visi.visit(tree)

		return [*map(lambda nn: nn.id, visi.names)]
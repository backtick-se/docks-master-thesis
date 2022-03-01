import ast

class Visitor(ast.NodeVisitor):
	def __init__(self):
		self.names = []

	# def visit_FunctionDef(self, node):
	# 	self.names.append(node.name)
	# 	self.generic_visit(node)
	
	# def visit_ClassDef(self, node):
	# 	self.visit_FunctionDef(node)
	
	# def visit_AsyncFunctionDef(self, node):
	# 	self.visit_FunctionDef(node)

	def generic_visit(self, node):
		try:
			if node.name: self.names.append(node.name)
		except:
			pass
		
		return super().generic_visit(node)

	@staticmethod
	def get_names(code: str):
		if code is None: return []

		tree = ast.parse(code)
		visi = Visitor()
		visi.visit(tree)

		return visi.names
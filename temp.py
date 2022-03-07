import ast

def try_parent(node):
	try:
		parent = node.parent
	except:
		parent = None

	return parent

class Visitor(ast.NodeVisitor):
	def __init__(self):
		# (name, superclasses)
		self.classes = []
		# (name, method owner)
		self.functions = []

	def visit_ClassDef(self, node):
		self.classes.append((node.name, [*map(lambda n: n.id, node.bases)], try_parent(node)))
		self.generic_visit(node)

	def visit_FunctionDef(self, node):
		self.functions.append((node.name, try_parent(node)))
		self.generic_visit(node)
	
	def visit_AsyncFunctionDef(self, node):
		self.visit_FunctionDef(node)

	@staticmethod
	def get_data(code: str):
		if code is None: return []

		tree = ast.parse(code)

		# Set parent node for all nodes
		for node in ast.walk(tree):
			for child in ast.iter_child_nodes(node):
				child.parent = node

		visi = Visitor()
		visi.visit(tree)

		return visi.classes, visi.functions
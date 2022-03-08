import ast

def try_parent(node):
	try:
		parent = node.parent
	except:
		parent = None

	return parent

def get_id(base):
	try:
		return base.id
	except:
		return base.attr

class Visitor(ast.NodeVisitor):
	def __init__(self):
		# (name, superclasses)
		self.classes = []
		# (name, owner)
		self.functions = []

	def visit_ClassDef(self, node):
		self.classes.append((node.name, [*map(get_id, node.bases)]))
		self.generic_visit(node)

	def visit_FunctionDef(self, node):
		parent = try_parent(node)

		if parent and type(parent) in [ast.ClassDef, ast.FunctionDef]:
			owner = parent.name
		else:
			owner = None

		self.functions.append((node.name, owner))
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
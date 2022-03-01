import ast

class Visitor(ast.NodeVisitor):
	def __init__(self):
		self.names = []
	
	def visit_Name(self, node):
		self.names.append(node)
		self.generic_visit(node)
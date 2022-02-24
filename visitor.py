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

		def process(node):
			name = node.name

			firstnode = node.body[0]
			isexpr = type(firstnode) is ast.Expr

			if isexpr and type(firstnode.value) is ast.Constant:
				node.body = node.body[1:]
			
			
			code = ast.unparse(node)
			
			return name, code

		return [*map(process, visi.functions)]
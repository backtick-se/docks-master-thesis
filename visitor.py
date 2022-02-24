import ast

class Visitor(ast.NodeVisitor):
	def __init__(self):
		self.functions = []

	def visit_FunctionDef(self, node):

		try:
			firstarg = node.args.args[0].arg
		except:
			firstarg = None

		# Skip methods
		if firstarg != 'self':
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

			# Extract docstring
			fnode = node.body[0]
			isexpr = type(fnode) is ast.Expr

			if isexpr and type(fnode.value) is ast.Constant:
				node.body = node.body[1:]

				docstr = fnode.value.value
				code = ast.unparse(node)
				return name, code, docstr
			
			return None

		return [*filter(lambda e: e != None, map(process, visi.functions))]
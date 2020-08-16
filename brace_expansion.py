from pasture_orthography import brace_delimiter, brace_key

# parse text as a concatenated expression
def parse_cat(text):
	parts = [] # the pieces that are concatenated
	chunk_stack = [] # the stack, each element representing open {} expressions with (starting index, key)
	i = 0
	while i < len(text):
		if text[i] == "{": 
			j = i + 1 # find the key of the expression, as some number of 's
			key = ""
			while text[j] == brace_key:
				key += text[j]
				j += 1
			i += len(key)
			chunk_stack.append((i,key))
		elif text[i] == "}": 
			if len(chunk_stack) == 0: raise
			elif len(chunk_stack) == 1: # pop from the stack and add to the list of parts
				parts.append(parse_or(text[chunk_stack[-1][0] + 1: i], chunk_stack[-1][1]))
			chunk_stack = chunk_stack[:-1]
		elif len(chunk_stack) == 0: 
			parts.append(text[i])
		i += 1
	return ("cat", parts)
			
# parse text as a list of options for the brace expansion
def parse_or(text, key):
	depth = 0 # number of {} expressions deep
	parts = []
	chunk_beginning = 0 # beginning of the current option
	for i in range(len(text)):
		if text[i] == "{": depth += 1
		elif text[i] == "}": 
			if depth == 0: raise
			else: depth -= 1
		if text[i] == brace_delimiter and depth == 0: # boundary between options
			parts.append(parse_cat(text[chunk_beginning: i]))
			chunk_beginning = i + 1
	parts.append(parse_cat(text[chunk_beginning:]))
	return ("or", key, parts)
	
# merge bindings b1 and b2, but return None if they conflict
def merge_bindings(b1, b2):
	for key in list(b1):
		if key in list(b2) and b2[key] != b1[key]: return None
	re = {}
	re.update(b1)
	re.update(b2)
	return re
	
# merge a list of possibilities (each possibility a (text, binding) pair), only concatenating where bindings don't conflict
def merge_possibilities(l1, l2):
	initial_merge, resolved_merge = [], []
	for i in l1:
		for j in l2:
			initial_merge.append( (i[0]+j[0], merge_bindings(i[1],j[1])) )
	for x in initial_merge:
		if x[1] is not None:
			resolved_merge.append(x)
	return resolved_merge
	#return [x for x in [(i[0]+j[0], merge_bindings(i[1],j[1])) for i in l1 for j in l2] if x[1] is not None]
	
def flatten(l):
	re = []
	for i in l: 
		for j in i:
			re.append(j)
	return re
	
def updated(d1, d2):
	re = {}
	re.update(d1)
	re.update(d2)
	return re
	
# turn an AST into a list of possibilities
def process(ast, bindings = {}):
	if type(ast) == str:
		return [(ast, bindings)]
	elif ast[0] == "cat":
		components = ast[1]
		if len(components) == 0: return [("", bindings)]
		merged = process(components[0], bindings)
		for component in components[1:]:
			f = process(component, bindings)
			merged = merge_possibilities(merged, f)
		return merged
	elif ast[0] == "or":
		key = ast[1]
		components = ast[2]
		if key == "":
			return flatten([process(component, bindings) for component in components])
		elif key in list(bindings):
			return process(components[bindings[key]], bindings)
		else:
			return flatten([process(components[i], updated(bindings, {key: i})) for i in range(len(components))])
			
def expand(text):
	return [x[0] for x in process(parse_cat(text))]
	

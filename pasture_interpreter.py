chars = {"line_delimiter": ";",
	"line_escape": "/",
	"assignment": "=>",
	"scope": "\t",
	"application": ".",
	"composition": " ",
	"delayed_application": ",",
	"argument": "$",
	"prior": "%",
	"comment_single": "#",
	"comment_multi": "##"}
	
def log(a):
	print(a+": ",eval(a))
chars_rev = {}

for k in list(chars):
	chars_rev[chars[k]] = k
	
def string(exp):
	if exp == []: return ""
	if exp[0] == "assignment": 
		return string(exp[1])+" "+chars[exp[0]]+" "+string(exp[2])
	if exp[0] == "application": 
		return "("+string(exp[1])+chars[exp[0]]+string(exp[2])+")"
	if exp[0] == "argument": 
		if len(exp) == 2: return chars[exp[0]]+string(exp[1])
		else: return chars[exp[0]]
	return exp[0]
	
# parse - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def group(text):

	text = chars["line_delimiter"].join(list(map(lambda s: s.replace("\n",""), text)))

	text = text.replace(chars["line_escape"] + chars["line_delimiter"], "") 

	text = text.split(chars["line_delimiter"])
	
	new_text = []
	for line in text:
		try: new_text.append(line[:line.index(chars["comment_single"])])
		except: new_text.append(line)
	
	return new_text
		
def tokenize(line):
	
	tokens = [line]
	
	for character in list(chars.values()) + list("()[]{}\""):
		t = []
		for token in tokens: 
			p = []
			for piece in token.split(character):
				p += [piece, character]
			t += p[:-1]
		tokens = t
			
	while '' in tokens: tokens.remove('')
	while len(tokens) > 1 and tokens[0] == " ": tokens.remove(" ")
	while len(tokens) > 1 and tokens[-1] == " ": tokens = tokens[:-1]
	
	#print("\n\n")
	#print("tokens:", tokens)
	return tokens
	
def flatten(l): 
	re = []
	for j in l: re.extend(j)
	return re
			
def ast_exp(exp):
	while len(exp) > 0 and exp[0] == " ": exp = exp[1:]
	while len(exp) > 0 and exp[-1] == " ": exp = exp[:-1]
	
	if exp == []: return []
	
	depths = []
	depth = 0
	all_one_part = True
	frozen = False
	for i in range(len(exp)):
		if exp[i] == "(" and not frozen: depth += 1
		elif exp[i] == ")" and not frozen: depth -= 1	
		if depth < 0: return None
		all_one_part = all_one_part and (depth > 0 or i == len(exp) - 1)
		depths.append(depth)
	
	if depths[-1] != 0: return None
	
	if all_one_part and len(exp) > 1: return ast_exp(exp[1:-1])
	
	#print()
	#print("exp:", exp)
	#print("depths:", depths)
	parts = []
	last_part = 0
	for i in range(len(exp)):
		if depths[i] == 0:
			parts.append(exp[last_part:i+1])
			last_part = i+1
			
	#print("parts:", parts)
	
	if len(parts) == 0: 
		return []
		
	if len(parts) == 1: 
		if parts[0][0] in list(chars_rev): return [chars_rev[parts[0][0]]]
		return parts[0]
		
	if len(parts) == 2 and parts[0] == [chars["argument"]]: return ["argument", parts[1]]
	
	operations = [part[0] for part in parts if part[0] == chars["application"] or part[0] == chars["delayed_application"]]
	operation_indexes = [i for i in range(len(parts)) if parts[i][0] == chars["application"] or parts[i][0] == chars["delayed_application"]]
	
	#print("operations:", operations)
	if operations[:-1] == chars["delayed_application"]: return None
	
	if len(operations) == 1 or operations[-2] == chars["application"]: 
		return ["application", ast_exp(flatten(parts[:operation_indexes[-1]])), ast_exp(flatten(parts[operation_indexes[-1]+1:]))]
		
	last_pos = -1
	for i in range(len(operations)): 
		if operations[i] == chars["delayed_application"] and (i == 0 or operations[i-1] == chars["application"]): last_pos = i
	if last_pos != -1:
		return ["application", ast_exp(flatten(parts[:operation_indexes[last_pos]])), ast_exp(flatten(parts[operation_indexes[last_pos]+1:]))]
	
	if len(operations) > 0:
		return ["application", ast_exp(flatten(parts[:operation_indexes[-1]])), ast_exp(flatten(parts[operation_indexes[-1]+1:]))]
	
	return None
	
def ast(line):
	try: i = line.index(chars["assignment"])
	except: 
		if line == []: return []
		return None
	tree = ["assignment", ast_exp(line[:i]), ast_exp(line[i+1:])]
	return tree

# eval - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def get_bindings(match, abstract):
	if abstract == ["argument"]: return {}
	if abstract[0] == "argument" and len(abstract) == 2: return {abstract[1][0]: match}
	if len(abstract) > 2:
		bindings = {}
		for i in range(1,len(match)):
			bindings.update(get_bindings(match[i], abstract[i]))
		return bindings
	return {}
	
def replace(exp, bindings):
	if len(exp) == 1 and exp[0] in list(bindings): return bindings[exp[0]]
	if type(exp) == list: return [replace(x, bindings) for x in exp]
	return exp

def evaluate(match, rule):
	bindings = get_bindings(match, rule[1])
	return replace(rule[2], bindings)

def match_expressions(concrete, abstract):
	if abstract[0] == "argument": return True
	if concrete[0] != abstract[0] or len(concrete) != len(abstract): return False
	re = True
	for i in range(1,len(concrete)):
		re = re and match_expressions(concrete[i], abstract[i])
	return re

def find_match(concrete, abstract):
	if match_expressions(concrete, abstract): return concrete
	if len(concrete) < 3: return None
	right = find_match(concrete[2], abstract)
	if right is not None: return right
	return find_match(concrete[1], abstract)
	
def update(exp, match, newval):
	if exp == match: return newval
	if type(exp) == list: return [update(x, match, newval) for x in exp]
	return exp
	
def step(exp, rules):
	for rule in rules:
		match = find_match(exp, rule[1])
		if match is not None:
			newval = evaluate(match, rule)
			return update(exp, match, newval)
	return exp
	
step_limit = 10000
			
def big_step(exp, rules):
	a = exp
	b = step(a, rules)
	steps_taken = 0
	while a != b:
		c = step(b, rules)
		a = b
		b = c
		steps_taken += 1
		print(string(a))
		if steps_taken > step_limit: return None
		
	return a

# do it - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

text = open("pasture.txt").readlines()
text = group(text)
lines = [a for a in [ast(tokenize(line.strip())) for line in text] if a != []]


boundary_text = open("pasture_boundary.txt").readlines()
boundary_text = group(boundary_text)
boundary_pairs = [(ast(tokenize(line[line.index(chars["assignment"])+len(chars["assignment"])].strip())), TODO) for line in boundary_text if line.strip() != ""]
boundary_lines = [a for a in [ast(tokenize(line.strip().split("=>")) for line in boundary_text] if a != []]

if lines == []: pass
else:
	expression = lines[-1][1]
	rules = lines[:-1]
	print("Rules:\n")
	for r in rules:
		print(string(r))
		
	print("\nEvaluation:\n")
	print(string(expression))
	new_expression = big_step(expression, rules)

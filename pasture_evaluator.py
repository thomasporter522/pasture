from pasture_orthography import string

# def get_bindings(match, abstract):
	# if abstract == ["argument"]: return {}
	# if abstract[0] == "argument" and len(abstract) == 2: return {abstract[1][0]: match}
	# if len(abstract) > 2:
		# bindings = {}
		# for i in range(1,len(match)):
			# bindings.update(get_bindings(match[i], abstract[i]))
		# return bindings
	# return {}
	
# def replace(exp, bindings):
	# if len(exp) == 1 and exp[0] in list(bindings): return bindings[exp[0]]
	# if type(exp) == list: return [replace(x, bindings) for x in exp]
	# return exp

# def match_expressions(concrete, abstract):
	# if abstract[0] == "argument": return True
	# if concrete[0] != abstract[0] or len(concrete) != len(abstract): return False
	# re = True
	# return replace(rule[2], bindings)

# def match_expressions(concrete, abstract):
	# if abstract[0] == "argument": 
		# if len(abstract) == 1: return True
		# return True
	# if concrete[0] != abstract[0] or len(concrete) != len(abstract): return False
	# re = True
	# for i in range(1,len(concrete)):
		# re = re and match_expressions(concrete[i], abstract[i])
	# return re

# # finds a place where the expression [concrete] matches the pattern expression [abstract]
# def find_match(concrete, abstract):
	# if match_expressions(concrete, abstract): return concrete
	# if len(concrete) < 3: return None
	# right = find_match(concrete[2], abstract)
	# if right is not None: return right
	# return find_match(concrete[1], abstract)
	
# # updates [exp] by replacing [match] with [newval]
# def update(exp, match, newval):
	# if exp == match: return newval
	# if type(exp) == list: return [update(x, match, newval) for x in exp]
	# return exp
	
# # take a small step evaluation of [exp] according to [rules], by:
# def step(exp, rules):
	# for rule in rules:
		# match = find_match(exp, rule[1]) # finding a rule in [rules] that matches [exp],
		# if match is not None:
			# bindings = get_bindings(match, rule[1]) # getting the bindings of that rule,
			# newval = replace(rule[2], bindings) # replacing the output of that rule according to the bindings,
			# return update(exp, match, newval) # and updating [exp] with that output where the match occurred 
	# return exp
	
# --------------
	
# attempts to match [exp] with [pattern]
# returns the generated bindings if successful, else returns None
def match(exp, pattern):
	
	if len(exp) == 1 and exp == pattern: return {}
	
	if pattern[0] == "argument":
		if len(pattern) == 1: return {}
		if len(pattern) == 2: return {pattern[1][0]: exp}
		else: return None
		
	if pattern[0] == "application":

		if type(exp) != list or exp[0] != "application": return None

		left = match(exp[1], pattern[1])
		right = match(exp[2], pattern[2])
		if None in [left, right]: return None

		conflicting_bindings = False
		for key in list(left):
			if key in list(right) and left[key] != right[key]: 
				conflicting_bindings = True

		if conflicting_bindings: return None
		left.update(right)
		return left
		
	return None
	
# recusursively replaces [exp] according to [bindings]
def replace(exp, bindings):
	if bindings is None: return None
	if exp[0] in list(bindings): return bindings[exp[0]]
	if type(exp) is list: return [replace(subexp, bindings) for subexp in exp]
	return exp
			
# attempts to apply [rule] to [exp]. 
# returns None if unsuccessful or (new expression, bindings) if successful
def direct_apply(exp, rule):
	return replace(rule[2], match(exp, rule[1])) 
	
	
# return None or new expression
def subexpression_apply(exp, rule):
	direct = direct_apply(exp, rule)
	if direct is not None: 
		return direct
	if len(exp) < 3: return None
	right = subexpression_apply(exp[2], rule)
	if right is not None: return [exp[0], exp[1], right]
	left = subexpression_apply(exp[1], rule)
	if left is not None: return [exp[0], left, exp[2]]
	return None
	
def step(exp, rules):
	for rule in rules:
		newexp = subexpression_apply(exp, rule)
		if newexp is not None:
			return newexp
	return exp
	
step_limit = 10000
			
# big step evaluate the epression [exp] according to [rules]
def evaluate(exp, rules):
	a = exp
	steps_taken = 0
	print(steps_taken, string(a))
	b = step(a, rules)
	while a != b:
		steps_taken += 1
		print(steps_taken, string(b))
		c = step(b, rules)
		a = b
		b = c
		assert steps_taken <= step_limit
		
	return a



from os import extsep
from pasture_orthography import string
	
# attempts to match [exp] with [pattern]
# returns the generated bindings if successful, otherwise None
def match(exp, pattern):
	#print("matching", exp, pattern)
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
		#print("Bindings", left)
		return left
		
	return None
	
# recusursively replaces [exp] according to [bindings]
def replace(exp, bindings):
	if bindings is None: return None
	if type(exp) is list: 
		if len(exp) > 1: return [exp[0]] + [replace(subexp, bindings) for subexp in exp[1:]]
		elif exp[0] in list(bindings): return bindings[exp[0]]
	return exp
			
# attempts to apply [rule] to [exp]. 
# returns (new expression, bindings) if successful, otherwise None
def direct_apply(exp, rule):
	return replace(rule[2], match(exp, rule[1])) 
	
# attempts to apply [rule] to some subexpression of [exp]. 
# returns new expression if successful, otherwise None
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
			#print("Rule applied:", string(rule))
			return newexp, rule
	return None, None
	
step_limit = 10000
rule_verbose = False
			
# big step evaluate the epression [exp] according to [rules]
def evaluate(exp, rules):
	steps_taken = 0
	rule = None
	while exp is not None:
		#print(exp)
		steps_taken += 1
		print(str(steps_taken)+": "+string(exp)+("" if rule is None or not rule_verbose else " ("+string(rule)+")"))
		exp, rule = step(exp, rules)
		assert steps_taken <= step_limit
	return exp

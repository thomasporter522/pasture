line_delimiter = ";"
line_escape = "/"
assignment = "=>"
application = " "
delayed_application = ","
argument = "$"
prior = "%"
comment_single = "#"
comment_begin = "#-"
comment_end = "-#"
brace_delimiter = "|"
brace_key = "'"
	
def verbose_string(exp, internal = False):
	if exp is None: return "None"
	if exp == []: return ""
	if exp[0] == "assignment": 
		assert len(exp) == 3
		return string(exp[1])+" "+assignment+" "+string(exp[2])
	if exp[0] == "application": 
		assert len(exp) == 3
		return "("+string(exp[1])+application+string(exp[2])+")"
	if exp[0] == "argument": 
		if len(exp) == 2: return argument+string(exp[1])
		elif len(exp) == 1: return eval(exp[0])
		else: raise
	assert len(exp) == 1
	return exp[0]
	
# internal specifies whether this call is internal to the method
# (and thus whether to return contextual information )
# caution specifies whether 
def string(exp, internal = False, first_arg = True):
		
	re = ""
	
	if exp is None: re = "None"
	
	elif exp == []: re = ""
	
	elif exp[0] == "assignment": 
		
		assert len(exp) == 3
		re = string(exp[1], True)+" "+assignment+" "+string(exp[2], True)
		
	elif exp[0] == "application": 
		
		assert len(exp) == 3
		
		re = None
		
		if type(exp[1]) is list and exp[1][0] == "application" and not first_arg:
			# if you add parens, you can pretend you are the first arg again 
			re = "("+string(exp[1], True, True)+")"	
		else: re = string(exp[1], True, first_arg)
		
		if type(exp[2]) is list and exp[2][0] == "application":
			re += delayed_application
		else: re += application
				
		return re + string(exp[2], True, False)
		
	elif exp[0] == "argument":
		 
		if len(exp) == 2: re = argument+string(exp[1], True)
		elif len(exp) == 1: re = eval(exp[0])
		else: raise
		
	else: 
		assert len(exp) == 1
		re = exp[0]
		
	if internal: return re#, {"applicative": False})
	return re

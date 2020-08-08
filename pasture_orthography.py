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
	
def string(exp):
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

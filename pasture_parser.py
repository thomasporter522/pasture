from brace_expansion import expand
from pasture_orthography import \
	line_delimiter, \
	line_escape, \
	assignment, \
	application, \
	delayed_application, \
	argument, \
	prior, \
	comment_single, \
	comment_begin, \
	comment_end, \
	string

tokens = [assignment, application, delayed_application, argument, prior]
	
# Return [text] but with all commented text removed
def remove_comments(text):
	
	noncomment_text = ""
	
	i = 0 # current index in the text string
	depth = 0 # current depth of nested multiline comments
	oneline_comment = False # whether current text is in a oneline comment 
	wait = False # true iff a comment just finished, but text shouldn't be considered valid yet
	
	while i < len(text):
		
		jump = 1 # number of spaces to step forward in the string (default is 1)
		
		if text[i:i+len(comment_begin)] == comment_begin: 
			depth += 1
			jump = len(comment_begin)
		elif text[i:i+len(comment_end)] == comment_end: 
			depth -= 1	
			wait = True
			jump = len(comment_end)
		elif text[i:i+len(comment_single)] == comment_single: 
			oneline_comment = True
			jump = len(comment_single)
		elif text[i:i+len(line_delimiter)] == line_delimiter: 
			oneline_comment = False
			jump = len(line_delimiter)
					
		if wait: wait = False # waiting only lasts one step
		elif depth == 0 and not oneline_comment: # add to noncomment text iff not in a multiline comment, not in a oneline comment, and not waiting
			noncomment_text += text[i]
		assert depth >= 0
		
		i += jump
		
	return noncomment_text
		
# transforms [text] from raw string to list of lines of code
def group(text):
	
	text = text.replace("\n",line_delimiter) # consistent line delimiter
	text = text.replace(line_escape + line_delimiter, "") # implement line continuation
	text = remove_comments(text) # remove commented text
	text = text.split(line_delimiter) # return list of lines
	text = flatten([expand(line) for line in text])
	return text
		
# transforms raw text of [line] into a list of tokens
def tokenize(line):
	tokenized_line = []
	
	i = 0
	token = ""
	while i < len(line):
		jump = 1
		token += line[i]
		for t in tokens + list("()"):
			if line[i:i+len(t)] == t:
				jump = len(t)
				if len(token) > 1: tokenized_line.append(token[:-1])
				token = ""
				tokenized_line.append(t)
		i += jump
		
	if len(token) > 0: tokenized_line.append(token)
	
	application_cleaned_line = [] # remove spaces that are not really application
	for i in range(len(tokenized_line)):
		if tokenized_line[i] == application and \
			(len(application_cleaned_line) == 0 \
			or application_cleaned_line[-1] == assignment \
			or i + 1 == len(tokenized_line) \
			or tokenized_line[i+1] in [application, assignment]
			or (i > 0 and tokenized_line[i-1] == delayed_application)
			or (i + 1 < len(tokenized_line) and tokenized_line[i+1] == delayed_application)): continue 
			# remove spaces at the beginning
			# remove spaces after assignment
			# remove spaces at the end
			# remove duplicate spaces, and spaces before assignment
			# remove spaces bordering delated application
		application_cleaned_line.append(tokenized_line[i])
	
	return application_cleaned_line
	
# flatten a list of lists
def flatten(l): 
	re = []
	for j in l: re.extend(j)
	return re
			
# return the ast of an expression
def ast_exp(exp):
	
	if exp == []: return []
	
	depths = [] # depths[i] is the depth in () at position [i] of [exp]
	depth = 0 # the current depth 
	all_one_part = True # whether exp is all one part (one parenthetical)
	for i in range(len(exp)):
		if exp[i] == "(": depth += 1
		elif exp[i] == ")": depth -= 1	
		all_one_part = all_one_part and (depth > 0 or i == len(exp) - 1)
		depths.append(depth)
		assert depth >= 0
	
	assert depths[-1] == 0 # no danlging parens
	
	if all_one_part and len(exp) > 1: return ast_exp(exp[1:-1]) # remove parens around (...)
	
	parts = [] # list of all parts (direct subexpressions)
	last_part = 0
	for i in range(len(exp)):
		if depths[i] == 0:
			parts.append(exp[last_part:i+1])
			last_part = i+1
				
	if len(parts) == 0: return []
		
	if len(parts) == 1: 
		if parts[0][0] == argument: return ["argument"]
		if parts[0][0] == prior: return ["prior"]
		return parts[0]
		
	if len(parts) == 2 and parts[0] == [argument]: return ["argument", parts[1]]
	
	operations = [part[0] for part in parts if part[0] in [application, delayed_application]]
	operation_indexes = [i for i in range(len(parts)) if parts[i][0] in [application, delayed_application]]
	
	assert operations[-1] != delayed_application
	
	if len(operations) == 1 or operations[-2] == application: 
		return ["application", ast_exp(flatten(parts[:operation_indexes[-1]])), ast_exp(flatten(parts[operation_indexes[-1]+1:]))]
		
	last_pos = -1
	for i in range(len(operations)): 
		if operations[i] == delayed_application and (i == 0 or operations[i-1] == application): last_pos = i
		
	if last_pos != -1:
		return ["application", ast_exp(flatten(parts[:operation_indexes[last_pos]])), ast_exp(flatten(parts[operation_indexes[last_pos]+1:]))]
	
	if len(operations) > 0:
		return ["application", ast_exp(flatten(parts[:operation_indexes[-1]])), ast_exp(flatten(parts[operation_indexes[-1]+1:]))]
	
	raise
	
# return the ast of a line of code (a rule)
def ast(line):
	if line == []: return []
	i = line.index(assignment)
	return ["assignment", ast_exp(line[:i]), ast_exp(line[i+1:])]

# return a list of rules, in abstract syntax tree form, specified by the pasture code in [text]
def parse(text):
	return list(filter(lambda x: x != [], [ast(tokenize(line)) for line in group(text)]))

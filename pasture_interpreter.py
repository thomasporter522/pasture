import pasture_parser as parser
import pasture_evaluator as evaluator
from pasture_orthography import string

import sys

if __name__ == "__main__":
	filename = "test_code/evaluation_example_0.txt"
	if len(sys.argv) > 1: filename = sys.argv[1]
	rules = parser.parse(open(filename).read())
	print("---Rules---")
	[print(string(rule)) for rule in rules]
	print("---Evaluation---")
	result = string(evaluator.evaluate(["main"], rules))
	#print(result)

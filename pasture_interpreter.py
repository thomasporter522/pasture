import pasture_parser as parser
import pasture_evaluator as evaluator
from pasture_orthography import string

import sys

if __name__ == "__main__":
	filename = "examples/example_2_list.pst"
	if len(sys.argv) > 1: filename = sys.argv[1]
	rules = parser.parse(open(filename).read())
	print("---Rules---")
	[print(string(rule)) for rule in rules]
	print("---Evaluation---")
	evaluator.evaluate(["main"], rules)

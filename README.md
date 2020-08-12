# Pasture
A simple language that takes functional programming beyond its logical extreme.

## Introduction
The pasture programming language's key innovation is treating functions and type constructors uniformly; both are symbols formally applied to other expressions, and reductions rules may simulate function definition. The language is also fundamentally typeless, with each expression being just a symbol or the formal application of one expression to another. 

Pasture is similar in spirit to lambda calculus, with function application as the central operation. 

Pasture is similar in spirit to Haskell or OCaml, employing currying and other functional programming covnentions, and treating complex data as structured with symbolic type constuctors.

Pasture is similar in spirit to LISP, following the 'code as data' paradigm and treating syntactic sugar, functions on data, and higher order functions uniformly.

Pasture is similar in spirit to symbolic programming, with all computation expressed as rewrite rules

Pasutre also embraces a 'left to right, top to bottom' philosophy, employing something like Lawvere's notation for category theory by writing functions to the right of their arguments. This means that the computation can be read left to right when it is the composition of many functions of low arity, but at the cost of greater confusion when dealing with few functions of high arity. 

Pasture is WILD. There is no type system, nor are variables, constants, functions, keywords, and data instrinsically distinct from each other. There are no runtime errors; any grammatical program will execute (except for space and time bounds). This places a huge burden on both the author and reader of pasture code, and probably dooms pasture to suffer from many of the problems of LISP. Pasture is far too extreme to be practical. My hope is just that pasture is interesting.

In short, pasture is a fusion of symbolic and functional programming. Computation is best written and thought of as function application, but secretly represents the application of rewrite rules _on trees of formal function application_.

## Tutorial

-- Coming soon --

## Specification

### Syntax 

A symbol can be any nonempty sequence of alphanumeric characters and '\_'. The role of strings in pasture is currently undetermined, so perhaps symbols will include quotation marks.

    expression ::= symbol  
      | (expression)  
      | expression expression  
      | expression,expression expression  
  
    pattern_symbol ::= $ | symbol | $symbol  

    pattern_expression ::= pattern_symbol   
      | (pattern_expression)  
      | pattern_expression pattern_expression  
      | pattern_expression,pattern_expression pattern_expression  

    rule ::= pattern_expression => expression  

    evaluation_context ::= '' | evaluation_context; rule  

A pasture file contains an evaluation context, and to 'execute' that file, the interpreter evaluates the special symbol 'main' in that context.

There are some modifications to this bare design:
- '#' starts a single line comment.
- '#-' starts, and '-#' ends, a multiline comment.
- A newline is equivalent to a ';' and the sequence '\\;' is equivalent to the empty string (allowing line continuation).
- There will be an extended form of brace expansion.

### Semantics

The space operation stands for left associative application: A B C D = (((A B) C) D)
The comma operation stands for "delayed application," which is essentially right associative application: A,B,C F = (A (B (C F))). I currently haven't figured out how to express the precedence of these two operators. Delayed application approximately binds tighter than non-delayed application, the exception being instances like A B C,D E = ((A B C) (D E)). The comma symbol was chosen because delayed application is often used to pass multiple arguments to a curried function. 

A pattern expression may match an expression and generate bindings. 
- $ matches any expression and generates no bindings (it's a wildcard). 
- $symbol matches any expression and produces the binding: symbol -> expression. 
- (pattern_expression0 pattern_expression1) matches (expression0 expression1) and produces bindings b iff pattern_expression0 matches expression0, producing bindings b0, and pattern_expression1 matches expression1, producing bindings b1, and b0 and b1 disagree nowhere (nothing is bound to different values between them), and b is the union of b0 and b1. 

A rule applies to an expression iff the input pattern_expression matches part of the expression. To apply a rule is to replace the matching subexpression with the output expression of the rule, replacing any symbols bound by the match. 

The evaluation of an expression according to an evaluation context is the reapeated application of the evaluation expression's rules, until no more rules match. That description begs the question of priority, in three distinct senses:
- When applying a certain rule to a certain expression, and multiple subexpressions match the rule, to which should the rule be applied? Interestingly to me, this question contains within it the dichotomy between call-by-value and call-by-name. If the priority in the expression goes from left (the argument) to right (the function), it results in behavior that simulates call-by-value evaluation. If the reverse is true, it would simulate call-by-name. Pasture searches the application tree depth first/preorder, from right to left, resulting in a call-by-name semantics.
- When applying a list of rules to a certain expression, and multiple rules match the expression, which should be applied to the expression? The current design is to simply give rules that appear earlier in the evaluation context precedence, but hopefully, later, more intelligent precedences can be deduced by the compiler, like placing strictly more general rules below strictly more specific.
- When applying a list of rules to a certain expression, and multiple rules can apply to multiple subexpressions of an expression, should the precedence ordering of the rules or the precedence ordering of the subexpressions take precedence? The answer is the former, since the selection of the subexpression depends on the selection of a rule, so to implement the latter would be awkward.
These issues of priority contain lots of room for exploration, and the initial decisions are by no means definitive.

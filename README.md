# Pasture
A simple language that takes functional programming beyond its logical extreme.

* [Introduction](#Introduction)
* [Tutorial](#Tutorial)
  * [Symbols](#Symbols)
  * [Expressions](#Expressions)
    * [Currying](#Currying)
    * [Delayed Application](#Delayed-Application)
  * [Rules](#Rules)
  * [Comments](#Comments)
  * [Brace Expansion](#Brace-Expansion)
* [Specification](#Specification)
  * [Syntax](#Syntax)
  * [Semantics](#Semantics)

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

Here is a less formal, more intuitive presentation of the language. It can be used in conjunction with the more formal specification below and the example code folder to get an idea of the pasture programming language. 

### Symbols

Computation may be generally thought of as symbol manipulation, where 'symbol' refers to an arbitrary distguishable entity, like a letter or word, with no inherent structure or meaning. The meaning of a collection of symbols is encoded in the structure of their assembly, paired with the rules for their manipulation. In pasture, data is stored as expressions of symbols. Symbols are strings of letters, numerals, and a few special characters like '\_'. They should generally represent ideas that are 'fundamental' in your program, and be atoms of your data. For example, let's make a program that adds 2 and 3 (albeit inefficiently). We can encode the natural numbers using the Peano method, with three symbols:

    0
    s
    +
    
Where ```0``` will stand for the number 0, ```s``` will stand for the successor function (the successor of n is 1+n), and ```+``` stands for the addition function. There is no notion of 'declaration' in pasture; these symbols will appear in our code without any other announcement of their nature. This is possible because all symbols are treated equally (barring special syntactic characters). Pasture does not know anything about these symbols, so it is up to the programmer to give the symbols meaning, as we shall see. 

### Expressions

Data in pasture is stored as an expression, which is a tree of symbols 'applied' to each other. An expression can either be a plain symbol, or an expression applied to another expression. The expression A applied to expression B is written ```B A``` or ```(B A)```. When stringing multiple applications together, from left to right, parentheses are inferred such: ```A B C D = ((A B) C) D```. The term "applied" is used here to suggest function application, but does not have any inherent behavior tied to it. It's an arbitrary, single, binary (two input) operation. What is A applied to B? It's just A applied to B. There's nothing more to be said. It's "formal" function application. So in our arithmetic system, here are some expressions:

    1. 0
    2. s
    3. s s
    4. 0 s
    5. 0 s s
    6. s 0
    7. b
    8. b s
    
In our interpretation of these expressions in terms of arithmetic, expression 1 represents the number 0. Expression 2 represents the successor function. Expression 3 doesn't make sense, since the successor function doesn't really have a successor. Expression 4 represents the number 1, expression 5 represents the number 2. Expression 6 doesn't make sense either, since we don't know what it means to apply 0 to anything. Expressions 7 and 8 don't make sense, because we don't know what ```b``` is. 

But pasture allows all of these expressions to exist, as well as things like ```(s 0 (0 0) a b)```. We can impose our interpretation of these expressions by writing rules.

#### Currying

An expression can only be applied to one other expression, so how do we deal with symbols representing functions that take in multiple arguments? The usual idiom is currying. When you curry a function like addition, you change it from a function that takes in two numbers and outputs one number, and turn it into a function that takes in one number (the first argument) and outputs a new function, which itself takes in one number (the second argument) and outputs one number (the result). So to symbolize the sum of ```A``` and ```B```, you can write ```A (B +)```.

#### Delayed Application

This occurs fairly frequently, along with other instances when you want to group the symbols right to left (such as ```1 (f inverse)``` to represent the inverse of f applied to 1). To reduce the parentheses needed, pasture introduces a new notation called 'delayed application' (symbolized by a comma). It essentially makes the parser 'wait' until the end of the the chain of commas to associate the symbols, and associates them from right to left. A few examples should illustrate the idea better than I can explain:

    a (b c) = a,b c
    a (b (c d)) = a,b,c d
    (a b) (c d) = a b,c d
    ((a b) c) (d (e f)) = a b c,d,e f
    (((a b) (c (d e))) f) (g (h i)) = a b,c,d e f,g,h i
    (a b) ((c d) e) = a b,(c d) e
    
So curried expressions can be naturally written like: ```1,2 +```.

### Rules

Rules are like lines of code in pasture, and govern the execution of the program. They determine how the computer manipulates symbols. Each rule is of the form ```pattern => output```. A pasture file evaluates an expression by applying the first rule it can, by matching a part of the expression with the pattern and replacing that subexpression with the output. Here is an example rule:

    0 s is_zero => false
    
This is like defining the function ```is_zero``` in the particular case of 1 (```0 s```). In the expression that the code is trying to simplify, anywhere there is an expression of the form ```0 s is_zero```, that gets replaced with the symbol ```false```. These rules of replacement are how we breathe life into the symbols, and grant them meaning. 

The output can also be a compound expression, like:

    0 s is_zero => true not
    
Depending on how your code is structured, and what you consider to be an atom. 

But patterns can be more than plain expressions. The ```$``` character matches any subexpression (it's a wildcard):

    $ s is_zero => false
    
This accounts for all the natural numbers except 0, as they are all expressed as the successor of something! The final component of pattern matching is bound matches, written as ```$something```:

    0,$x + => x
    $x s,$y + => x,y + s
    
The ```$x``` still matches anything, but that anything is then bound to the word ```x```, and replaces ```x``` in the output expression. These bindings can be used to restrict the matches, since all bound wildcards have to match for the pattern to match. The basic way to express this is the definition of the equals operation in pasture:

    $x,$x = => true
    
Newlines or semicolons separate rules, with ```\``` allowing line continuation:

    a => b
    b => c; c => d
    d \
    => e
    
And that's essentially it! Figure out the symbols you need to express data in your program, and write rules for manipulating expressions. A program runs by evaluating the expression ```main``` in your program. The only details left to understanding pasture are the comments and brace expansion (see below), and the order of precedence of pattern matching (see the specification section below). 

### Comments

A ```#``` character starts a comment that extends to the end of the line (until the next newline or ```;``` that doesn't have a ```\``` before it). ```#-``` and ```-#``` enclose arbitrary comments, and stack (in ```#-a#-b-#c-#```, everything is commented out). You can even use these to extend a line by commenting out the newline character!

    a => #-
    -# b

### Brace Expansion

Pasture includes an extended form of brace expansion, a system most commonly found in BASH. In other programming languages, like Scala, you might want to import many things from the same library, using:
    
    import library.{part1, part2, part3}
    
Which essentially expands into three lines (in Scala):

    import library.part1
    import library.part2
    import library.part3
    
This is a great feature. The brace expansion in BASH takes this idea further, allowing you to use such expansion anywhere in the code, and also allowing braces to be nested:

    a{b,c{d,e}f}g
    
Expands to (traditionally):

    abg
    acdfg
    acefg
 
Another feature of many programming languages, like python, is multiple assignment: 

    x,y = a,b
    
Expands to (traditionally):

    x = a
    y = b
    
But brace expansion, in it traditional form, cannot accomplish this:

    {x,y} = {a,b}

Expands to (traditionally):

    x = a
    x = b
    y = a
    y = b

My solution is to introduce 'linked' braces. Each pair of braces has a key, given by the number of ' characters immediately after the first brace. Any sets of braces with a (nonempty) key are 'linked.' The strings produced by expanding an expression with braces are only those for which the index of the 'choice' of that string agrees within all sets of linked braces. Here is an example (note that in pasture, | separates brace expansion options):

    {'x|y} = {'a|b}
    
Expands to (in pasture):

    x = a
    y = b
    
The first string corresponds to choosing the first option of all single ' brace expressions, the second string to choosing the second options. The string 'y = a' is disallowed because the 'y' indicates a choice of 'second' on the first brace expression, and the 'a' indicates a choice of 'first' on the second. Here's another example to make things clearer:

    {'a|b}{c|{'d|e}}

Expands to:

    ac
    ad
    bc
    be
    
It's a bit subtle, but it is ultimately extremely powerful. And it is so convenient as to be essentially necessary in pasture, where expressing multiple functions on the same object is common:

    human,horse with_the_torso_of {'{is_mythical | is_alive} | breathes_underwater} => {'true | false}
    
This pasture code expresses three things about a centaur (a horse with the torso of a human), and is probably preferable to writing out ```human,horse with_the_torso_of``` three times.

Brace expansion will occur on each line in the file, before any other parsing, and must result in a list of rules.

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
- There is an extended form of brace expansion.

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


    
 

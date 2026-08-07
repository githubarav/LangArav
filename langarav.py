from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageDraw, ImageOps, ImageChops, ImageStat, ImageColor
import random
from rembg import remove
import numpy as np
import cv2
from collections import ChainMap
#The symbols 
tEquals = "EQUALS"
tIdentifier = "IDENTIFIER"
tLParen = "LPAREN"
tRParen = "RPAREN"
tLSquare_Paren = "LSQUARE_PAREN"
tRSquare_Paren = "RSQUARE_PAREN"
tRSquigly_Paren = "RSQUIGLY_PAREN"
tLSquigly_Paren = "LSQUIGLY_PAREN"
tComma  = "COMMA"
tColon = "COLON"
tGreater = "GREATER"
tLess = "LESS"
tPlus = "PLUS"
tMinus = "MINUS"
tStar = "STAR"
tSlash = "SLASH"
tMod = "MOD"
tString = "STRING"
tNewline = "NEWLINE"
tIndent = "INDENT"
tDedent = "DEDENT"
tEOF = "EOF"
tInt = "INT"
tFloat = "FLOAT"
tDot = "DOT"

#The Keywords
tAnd = "AND"
tOr = "OR"
tNot = "NOT"
tIf = "IF"
tElif = "ELIF"
tElse = "ELSE"
tClass = "CLASS"
tFunc = "FUNC"

#built-in-functions
tLoad = "LOAD"
tBlend = "BLEND"
tPrint = "PRINT"

keywords = {
    "and": tAnd,
    "or": tOr,
    "not": tNot,
    "if": tIf,
    "elif": tElif,
    "else": tElse,
    "class": tClass,
    "func": tFunc
}

built_in_functions = {
    "load": tLoad,
    "blend": tBlend,
    "print": tPrint
    # add stuff like "print": tPrint, here and then create tPrint = "PRINT" above only if it is supposed to be written in the code like this print("x")
}


class Token:
    def __init__(self, type, value = None):
        self.type = type
        self.value = value
    def __repr__(self): 
        if self.value:
            return "{}:{}".format(self.type, self.value)
        else:
            return "{}".format(self.type)

def lexer(text):
    count = 0
    tokens = []
    indent_stack = [0]  # Tracks space counts (starts at baseline 0)
    at_line_start = True # Tracks whether we are at the beginning of a new line

    while count < len(text):
        current_char = text[count] 
        if current_char in ' \t':
            count += 1

        # ==========================================
            # NEWLINE & INDENTATION HANDLING
            # ==========================================
        elif current_char == "\n":
            tokens.append(Token(tNewline))
            count += 1
                
            # Calculate leading spaces on the next line
            indent_level = 0
            while count < len(text) and text[count] in " \t":
            # Count 4 spaces per tab or 1 space per ' '
                if text[count] == "\t":
                    indent_level += 4
                else:
                    indent_level += 1
                    count += 1

                # Ignore blank lines or comments completely
            if count < len(text) and text[count] in "\n#":
                continue

            current_indent = indent_stack[-1]

            # CASE 1: Indentation increased
            if indent_level > current_indent:
                indent_stack.append(indent_level)
                tokens.append(Token(tIndent))

            # CASE 2: Indentation decreased
            elif indent_level < current_indent:
                while indent_stack and indent_level < indent_stack[-1]:
                    indent_stack.pop()
                    tokens.append(Token(tDedent))
                    
                # Error check: Indent level must match a previous level in stack
                if indent_stack[-1] != indent_level:
                    raise IndentationError(f"Unindent does not match any outer indentation level at char {count}")

        elif current_char.isalpha() or current_char == "_":

            word = ""

            while count < len(text) and (text[count].isalnum() or text[count] == "_"):
                word += text[count]
                count += 1

            if word in keywords:
                tokens.append(Token(keywords[word]))

            elif word in built_in_functions:
                tokens.append(Token(built_in_functions[word])) 

            else:
                tokens.append(Token(tIdentifier, word))

        elif current_char == "=":
            tokens.append(Token(tEquals))
            count += 1

        elif current_char == ",":
            tokens.append(Token(tComma))
            count += 1

        elif current_char == ":":
            tokens.append(Token(tColon))
            count += 1

        elif current_char == ">":
            tokens.append(Token(tGreater))
            count += 1

        elif current_char == "<":
            tokens.append(Token(tLess))
            count += 1

        elif current_char == "+":
            tokens.append(Token(tPlus))
            count += 1

        elif current_char == "-":
            tokens.append(Token(tMinus))
            count += 1

        elif current_char == "*":
            tokens.append(Token(tStar))
            count += 1

        elif current_char == "/":
            tokens.append(Token(tSlash))
            count += 1

        elif current_char == "%":
            tokens.append(Token(tMod))
            count += 1

        elif current_char == "(":
            tokens.append(Token(tLParen))
            count += 1

        elif current_char == '"':
            count += 1
            image_file = ""
            while count < len(text) and text[count] != '"':
                image_file += text[count]
                count += 1
            count += 1
            tokens.append(Token(tString, image_file))

        elif current_char == ")":
            tokens.append(Token(tRParen))
            count += 1

        # Numbers (Ints and Floats)
        elif current_char.isdigit():
            num_str = ""
            dot_count = 0

            while count < len(text) and (text[count].isdigit() or text[count] == '.'):
                if text[count] == '.':
                    if dot_count == 1:
                        break # Second dot found, stop reading the number!
                    dot_count += 1
                
                num_str += text[count]
                count += 1

            if dot_count == 0:
                tokens.append(Token(tInt, int(num_str)))
            else:
                tokens.append(Token(tFloat, float(num_str)))

        elif current_char == ".":
            tokens.append(Token(tDot))
            count += 1

        elif current_char == "[":
            tokens.append(Token(tLSquare_Paren))
            count += 1

        elif current_char == "]":
            tokens.append(Token(tRSquare_Paren))
            count += 1

        elif current_char == "{":
            tokens.append(Token(tLSquigly_Paren))
            count += 1

        elif current_char == "}":
            tokens.append(Token(tRSquigly_Paren))
            count += 1

        elif current_char == "#":
            # Skip everything until the end of the line
            while count < len(text) and text[count] != "\n":
                count += 1
        
        else:
            raise Exception(f"Unexpected character: {current_char}")
    # ==========================================
    # EOF CLEANUP: Close all open indent scopes
    # ==========================================
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token(tDedent))

    tokens.append(Token(tEOF))
    return tokens

class StringNode:
    def __init__(self, value):
        self.value = value # the text

    def __repr__(self):
        return f'String("{self.value}")'

class IntNode:
    def __init__(self, value):
        self.value = value # the number
    def __repr__(self):
        return f'Int({self.value})'

class FloatNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'Float({self.value})'

class VarNode:
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f'Var({self.value})'

class FunctionCallNode:
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args
    def __repr__(self):
        return f'FunctionCall("{self.func_name}", {self.args})'

class FunctionDefNode:
    def __init__(self, name, body):
        self.name = name
        self.body = body  # This will hold the list of statements inside the function

class AssignNode:
    def __init__(self, var_node, value_node):
        self.var_node = var_node
        self.value_node = value_node
    
    def __repr__(self):
        return f'Assign({self.var_node} = {self.value_node})'

class ListNode:
    def __init__(self, elements):
        self.elements = elements  # List of AST nodes [expr, expr, ...]

    def __repr__(self):
        return f"ListNode({self.elements})"

class DictNode:
    def __init__(self, pairs):
        self.pairs = pairs  # List of (key_node, value_node) tuples

    def __repr__(self):
        return f"DictNode({self.pairs})"

class ClassDefNode:
    def __init__(self, name, body, parent=None):
        self.name = name          # Class name (e.g. "Aura")
        self.body = body          # List of statements returned by parse_block()
        self.parent = parent      # Optional base class name (e.g. "ParentClass")

    def __repr__(self):
        return f"ClassDefNode({self.name}, parent={self.parent}, body={self.body})"

class MethodCallNode:
    def __init__(self, target_node, method_name, args):
        self.target_node = target_node
        self.method_name = method_name
        self.args = args

    def __repr__(self):
        return f'MethodCall({self.target_node}.{self.method_name}({self.args}))'

# Represents a condition check like: x > 5 or x and y
class BinaryOpNode:
    def __init__(self, left, op, right):
        self.left = left    # e.g., VarNode("x")
        self.op = op        # e.g., ">", "AND", "OR"
        self.right = right  # e.g., IntNode(5)
    def __repr__(self):
        return f"BinaryOp({self.left} {self.op} {self.right})"

# Represents a 'not' condition like: not x
class UnaryOpNode:
    def __init__(self, op, expr):
        self.op = op        # "NOT"
        self.expr = expr    # Expression being negated
    def __repr__(self):
        return f"UnaryOp({self.op} {self.expr})"

# Represents an if / elif / else block
class IfNode:
    def __init__(self, condition, body, elif_blocks=None, else_body=None):
        self.condition = condition  # e.g., BinaryOpNode
        self.body = body            # List of statements inside 'if'
        self.elif_blocks = elif_blocks if elif_blocks else [] # List of (condition, body) tuples
        self.else_body = else_body  # List of statements inside 'else'
    def __repr__(self):
        return f"If(Cond: {self.condition}, Body: {self.body}, Elifs: {self.elif_blocks}, Else: {self.else_body})"

class BlockNode:
    def __init__(self, statements):
        self.statements = statements 

    def __repr__(self):
        return f"BlockNode({self.statements})"
    
class ProgramNode:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode({self.statements})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # Returns the current token we are looking at
    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    # Checks if current token matches the expected type, moves forward, and returns it
    def eat(self, token_type):
        token = self.current_token()
        if token and token.type == token_type:
            self.pos += 1
            return token
        else:
            raise SyntaxError(f"Expected {token_type}, but got {token.type if token else 'EOF'}")

    def parse_value(self):
        tok = self.current_token()
        if not tok:
            raise SyntaxError("Unexpected end of input")

        if tok.type == tLSquare_Paren:
            return self.parse_list()

        # --- Dictionary Parsing ---
        elif tok.type == tLSquigly_Paren:
            return self.parse_dict()

        # 1. Handle Built-In Functions (e.g. load("photo.jpg"))
        if tok.type in built_in_functions.values():
            func_token = self.eat(tok.type)
            args = self.parse_arguments()
            return FunctionCallNode(func_token.type, args)

        elif tok.type == tString:
            self.eat(tString)
            return StringNode(tok.value)

        elif tok.type == tInt:
            self.eat(tInt)
            return IntNode(tok.value)

        elif tok.type == tFloat:
            self.eat(tFloat)
            return FloatNode(tok.value)

        # 2. Handle Identifiers AND Method Calls (e.g. y or y.method(...))
        elif tok.type == tIdentifier:
            var_token = self.eat(tIdentifier)

            # 1. Is it a function call or class instantiation? (e.g., Aura() or print())
            if self.current_token() and self.current_token().type == tLParen:
                args = self.parse_arguments()
                var_node = FunctionCallNode(var_token.value, args)
            else:
                var_node = VarNode(var_token.value)

            # 2. Is it followed by dot access? (e.g., Aura.x, a.x, or img.circle(5))
            while self.current_token() and self.current_token().type == tDot:
                self.eat(tDot)
                method_token = self.eat(tIdentifier)

                # Only parse arguments if there are parentheses (e.g., img.circle(5))
                if self.current_token() and self.current_token().type == tLParen:
                    args = self.parse_arguments()
                else:
                    args = []  # Just attribute access (e.g., Aura.x or a.x)

                var_node = MethodCallNode(var_node, method_token.value, args)

            return var_node

        else:
            raise SyntaxError(f"Unexpected value token: {tok}")

    def parse_arguments(self):
        args = []
        self.eat(tLParen)

        # Handles Arguments

        if self.current_token() and self.current_token().type != tRParen:
            args.append(self.parse_value())

            while self.current_token() and self.current_token().type == tComma:
                self.eat(tComma) # Consume ','
                args.append(self.parse_value())

        self.eat(tRParen)
        return args

    # Add this inside your Parser class
    def parse_function_def(self):
        self.eat(tFunc)               # Eat 'func'
        func_name = self.current_token().value
        self.eat(tIdentifier)                 # Eat the function name

        self.eat(tLParen)             # Eat '('
        # (If you want parameters later, you'd parse them here)
        self.eat(tRParen)             # Eat ')'
        
        self.eat(tColon)              # Eat ':'

        # Parse the body of the function. 
        # Replace 'self.parse_block()' with whatever method you use to 
        # parse the indented block or statements under an if-statement/class.
        # If it's just a single statement for now, use [self.parse_statement()]
        body = self.parse_block()     

        return FunctionDefNode(func_name, body)

    # 1. Parse 'not' expressions
    def parse_unary(self):
        tok = self.current_token()
        if tok and tok.type == tNot:
            self.eat(tNot)
            return UnaryOpNode("NOT", self.parse_unary())
        return self.parse_value()

    def parse_factor(self):
        left = self.parse_unary()

        while self.current_token() and self.current_token().type in (tStar, tSlash, tMod):
            op_token = self.eat(self.current_token().type)
            right = self.parse_unary()
            left = BinaryOpNode(left, op_token.type, right)

        return left

    def parse_term(self):
        left = self.parse_factor()

        while self.current_token() and self.current_token().type in (tPlus, tMinus):
            op_token = self.eat(self.current_token().type)
            right = self.parse_factor()
            left = BinaryOpNode(left, op_token.type, right)

        return left    

    # 2. Parse comparisons like x > 5 or x < 10
    def parse_comparison(self):
        left = self.parse_term()
        
        tok = self.current_token()
        if tok and tok.type in (tGreater, tLess):
            op_token = self.eat(tok.type)
            right = self.parse_unary()
            return BinaryOpNode(left, op_token.type, right)
            
        return left

    # Parses lists like [1, 2, "hello"]
    def parse_list(self):
        self.eat(tLSquare_Paren)
        elements = []

        # If not an empty list []
        if self.current_token() and self.current_token().type != tRSquare_Paren:
            elements.append(self.parse_expression())

            while self.current_token() and self.current_token().type == tComma:
                self.eat(tComma)
                # Allow trailing commas like [1, 2,]
                if self.current_token() and self.current_token().type == tRSquare_Paren:
                    break
                elements.append(self.parse_expression())

        self.eat(tRSquare_Paren)
        return ListNode(elements)

    # Parses dictionaries like {"key": "value", "a": 10}
    def parse_dict(self):
        self.eat(tLSquigly_Paren)
        pairs = []

        # If not an empty dictionary {}
        if self.current_token() and self.current_token().type != tRSquigly_Paren:
            key = self.parse_expression()
            self.eat(tColon)
            val = self.parse_expression()
            pairs.append((key, val))

            while self.current_token() and self.current_token().type == tComma:
                self.eat(tComma)
                # Allow trailing commas like {"a": 1,}
                if self.current_token() and self.current_token().type == tRSquigly_Paren:
                    break
                key = self.parse_expression()
                self.eat(tColon)
                val = self.parse_expression()
                pairs.append((key, val))

        self.eat(tRSquigly_Paren)
        return DictNode(pairs)

    # Helper method to parse an entire indented block of statements
    def parse_block(self):
        statements = []

        # Consume optional newline after the colon before INDENT
        if self.current_token() and self.current_token().type == tNewline:
            self.eat(tNewline)

        # Eat the INDENT token opening the block scope
        self.eat(tIndent)

        # Parse statements until we hit DEDENT or end of file
        while self.current_token() and self.current_token().type not in (tDedent, tEOF):
            # Skip blank lines inside the block
            if self.current_token().type == tNewline:
                self.eat(tNewline)
                continue

            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        # Eat the DEDENT token closing the block scope
        if self.current_token() and self.current_token().type == tDedent:
            self.eat(tDedent)

        return statements

    def parse_class_def(self):
        self.eat(tClass) # Eat 'class' keyword
        
        # 1. Grab class name
        class_name_token = self.eat(tIdentifier)
        class_name = class_name_token.value

        parent_name = None
        # 2. Handle optional inheritance: class Child(Parent):
        if self.current_token() and self.current_token().type == tLParen:
            self.eat(tLParen)
            parent_token = self.eat(tIdentifier)
            parent_name = parent_token.value
            self.eat(tRParen)

        self.eat(tColon)
        
        # 3. Parse the entire indented class body
        body = self.parse_block()

        return ClassDefNode(class_name, body, parent_name)

    def parse_if_statement(self):
        # 1. Parse the main 'if' condition and colon
        condition = self.parse_expression()
        self.eat(tColon)
        
        # 2. Parse the entire 'if' indented block
        if_body = self.parse_block()

        elif_blocks = []
        else_body = None

        # 3. Handle 'elif' blocks (0 or more)
        while self.current_token() and self.current_token().type == tElif:
            self.eat(tElif)
            elif_cond = self.parse_expression()
            self.eat(tColon)
            elif_body = self.parse_block()
            elif_blocks.append((elif_cond, elif_body))

        # 4. Handle 'else' block (0 or 1)
        if self.current_token() and self.current_token().type == tElse:
            self.eat(tElse)
            self.eat(tColon)
            else_body = self.parse_block()

        return IfNode(condition, if_body, elif_blocks, else_body)

    # 3. Parse boolean expressions with 'and' / 'or'
    def parse_expression(self):
        left = self.parse_comparison()

        while self.current_token() and self.current_token().type in (tAnd, tOr):
            op_token = self.eat(self.current_token().type)
            right = self.parse_comparison()
            left = BinaryOpNode(left, op_token.type, right)

        return left

    def parse(self):
        statements = []

        while self.current_token() is not None and self.current_token().type != tEOF:
            # Skip empty lines or trailing newlines
            if self.current_token().type in (tNewline, tDedent):
                self.eat(self.current_token().type)
                continue

            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

            # Cleanly consume tEOF if present
        if self.current_token() and self.current_token().type == tEOF:
            self.eat(tEOF)

        return ProgramNode(statements)

    def parse_statement(self):
        tok = self.current_token()

        if not tok:
            return None

        elif tok.type == tClass:
            return self.parse_class_def()

        elif tok.type == tFunc:
            return self.parse_function_def()
        
        # Handle keywords like load("photo.jpg") directly
        elif tok.type in built_in_functions.values():
            func_token = self.eat(tok.type)
            args = self.parse_arguments()
            return FunctionCallNode(func_token.type, args)

        elif tok.type == tIf:
            self.eat(tIf)
            return self.parse_if_statement()

        # Handle lines starting with an Identifier (like img)
        elif tok.type == tIdentifier:
            var_token = self.eat(tIdentifier)
            var_node = VarNode(var_token.value)

            if self.current_token() and self.current_token().type == tLParen:
                args = self.parse_arguments()
                return FunctionCallNode(var_token.value, args)

            # Scenario B: Variable Assignment -> img = load(...)
            elif self.current_token() and self.current_token().type == tEquals:
                self.eat(tEquals)
                right_side = self.parse_expression() # Parses load(...)
                return AssignNode(var_node, right_side)

            # Scenario C: Method Call -> img.blur(5)
            elif self.current_token() and self.current_token().type == tDot:
                self.eat(tDot) # Consume '.'
                method_token = self.eat(tIdentifier) # Grab "blur", "grayscale", etc.
                args = self.parse_arguments()
                return MethodCallNode(var_node, method_token.value, args)

            # Just a bare variable
            return var_node

        return None

class Interpreter:
    def __init__(self):
        # Stores variables: e.g., {'x': 10, 'img': <LoadedImage object>}
        self.variables = {}

    def visit(self, node):
        #Dynamic dispatcher: routes each node to its specific visit method.
        # 🛠️ Safety check: If node is None, do nothing and return None
        if node is None:
            return None
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visit_{type(node).__name__} method defined.")
    
    def visit_IntNode(self, node):
        return node.value
    
    def visit_FloatNode(self, node):
        return node.value
    
    def visit_StringNode(self, node):
        return node.value

    def visit_VarNode(self, node):
        var_name = node.value
        if var_name in self.variables:
            return self.variables[var_name]
        raise NameError(f"Undefined variable '{var_name}'")

    def visit_ProgramNode(self, node):
        result = None
        for statement in node.statements:
            result = self.visit(statement)
        return result  # Returns the result of the last statement

    def visit_AssignNode(self, node):
        var_name = node.var_node.value
        val = self.visit(node.value_node)
        self.variables[var_name] = val
        return val
    
    def visit_ClassDefNode(self, node):
        print(f"[ENGINE - LANGUAGE] Defining class '{node.name}'...")

        class_namespace = {}

        # 1. Resolve parent class for inheritance
        bases = ()
        if getattr(node, 'parent', None):
            if node.parent in self.variables:
                parent_class = self.variables[node.parent]
                if isinstance(parent_class, type):
                    bases = (parent_class,)
                else:
                    raise TypeError(f"'{node.parent}' is not a valid class to inherit from.")
            else:
                raise NameError(f"Parent class '{node.parent}' is not defined.")

        # 2. Scope management: writes go to class_namespace, reads fallback to global
        saved_variables = self.variables
        self.variables = ChainMap(class_namespace, saved_variables)

        # Execute all statements in the class body
        for statement in node.body:
            self.visit(statement)

        # Restore global scope
        self.variables = saved_variables

        # Clean string representation for class instances
        class_namespace['__repr__'] = lambda self_inst: f"<{node.name} instance>"

        # 3. Create class and store in global variables
        new_class = type(node.name, bases, class_namespace)
        self.variables[node.name] = new_class
        return new_class

    # Add this to your Interpreter class
    def visit_FunctionDefNode(self, node):
        # We save the function in our variables dictionary as a custom dictionary.
        # This way the interpreter knows it's a user-defined function.
        self.variables[node.name] = {
            'type': 'function',
            'body': node.body
        }
        return None

    def visit_BinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        is_left_img = isinstance(left, Image.Image)
        is_right_img = isinstance(right, Image.Image)

        # --- CASE 1: Image + Image (Pixel Math) ---
        if is_left_img and is_right_img:
            arr1 = np.array(left.convert("RGB"))
            arr2 = np.array(right.convert("RGB"))
            
            # Ensure dimensions match
            if arr1.shape != arr2.shape:
                arr2 = cv2.resize(arr2, (arr1.shape[1], arr1.shape[0]))

            if node.op == tPlus:
                # cv2.add automatically clips values at 255 (no overflow wrap-around)
                return Image.fromarray(cv2.add(arr1, arr2))
            elif node.op == tMinus:
                # cv2.subtract clips values at 0
                return Image.fromarray(cv2.subtract(arr1, arr2))
            elif node.op == tStar:
                # Multiply pixel matrices
                res = cv2.multiply(arr1.astype(np.float32), arr2.astype(np.float32), scale=1.0/255.0)
                return Image.fromarray(res.astype(np.uint8))

        # --- CASE 2: Image + Variable/Number (e.g. img + x) ---
        elif is_left_img or is_right_img:
            img = left if is_left_img else right
            val = right if is_left_img else left

            if not isinstance(val, (int, float)):
                raise TypeError(f"Cannot perform math between Image and type {type(val)}")

            arr = np.array(img.convert("RGB"))
            
            if node.op == tPlus:
                # Add scalar value to all color channels
                scalar_arr = np.full(arr.shape, val, dtype=np.uint8)
                return Image.fromarray(cv2.add(arr, scalar_arr))
            elif node.op == tMinus:
                scalar_arr = np.full(arr.shape, val, dtype=np.uint8)
                return Image.fromarray(cv2.subtract(arr, scalar_arr))
            elif node.op == tStar:
                res = arr.astype(np.float32) * (val / 255.0 if val > 1 else val)
                return Image.fromarray(np.clip(res, 0, 255).astype(np.uint8))
            elif node.op == tSlash:
                res = arr.astype(np.float32) / max(val, 0.001)
                return Image.fromarray(np.clip(res, 0, 255).astype(np.uint8))

        # --- CASE 3: Standard Variable / Number Math (e.g. x = 9) ---
        if node.op == tPlus:
            return left + right
        elif node.op == tMinus:
            return left - right
        elif node.op == tStar:
            return left * right
        elif node.op == tSlash:
            return left / right
        elif node.op == tMod:
            return left % right
        elif node.op == tGreater:
            return left > right
        elif node.op == tLess:
            return left < right
        elif node.op == tAnd:
            return left and right
        elif node.op == tOr:
            return left or right

    def visit_UnaryOpNode(self, node):
        val = self.visit(node.expr)
        if node.op == "NOT" or node.op == tNot:
            return not val

    def visit_ListNode(self, node):
        return [self.visit(elem) for elem in node.elements]

    def visit_DictNode(self, node):
        return {self.visit(key): self.visit(val) for key, val in node.pairs}

    def visit_IfNode(self, node):
        # 1. Check main 'if' condition
        if self.visit(node.condition):
            for stmt in node.body:
                self.visit(stmt)
            return

        # 2. Check 'elif' blocks
        for elif_cond, elif_body in node.elif_blocks:
            if self.visit(elif_cond):
                for stmt in elif_body:
                    self.visit(stmt)
                return

        # 3. Fallback to 'else'
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
    
    def visit_FunctionCallNode(self, node):
        args = [self.visit(arg) for arg in node.args]

        # A. Handle Class Instantiation: a = Aura()
        if node.func_name in self.variables and isinstance(self.variables[node.func_name], type):
            cls = self.variables[node.func_name]
            return cls(*args)  # Instantiates class instance!

        elif node.func_name in self.variables and isinstance(self.variables[node.func_name], dict):
            if self.variables[node.func_name].get('type') == 'function':
                # Grab the saved AST nodes and run them!
                body = self.variables[node.func_name]['body']
                
                # Execute each statement in the function body
                for stmt in body:
                    self.visit(stmt)
                    
                return None

        elif node.func_name == tLoad or node.func_name == "LOAD":
            file_path = args[0]
            try:
                # Real side effect: Open image using Pillow!
                img = Image.open(file_path)
                print(f"[ENGINE] Successfully loaded image '{file_path}' ({img.size[0]}x{img.size[1]}px)")
                return img
            except FileNotFoundError:
                raise FileNotFoundError(f"[ENGINE ERROR] Could not find image file at '{file_path}'")

        elif node.func_name in self.variables and isinstance(self.variables[node.func_name], type):
            cls = self.variables[node.func_name]
            return cls(*args)

        # --- Multi-Image Blending ---
        elif node.func_name == tBlend or node.func_name == "BLEND":
            img1, img2 = args[0], args[1]
            alpha = float(args[2]) if len(args) > 2 else 0.5
            # Make sure both images are the same size before blending
            img2_resized = img2.resize(img1.size)
            return Image.blend(img1.convert("RGB"), img2_resized.convert("RGB"), alpha)

        elif node.func_name == tPrint or node.func_name == "PRINT":
            print(*args)
            return None

        raise NameError(f"Unknown function '{node.func_name}'")

    def visit_MethodCallNode(self, node):
        target = self.visit(node.target_node) # Resolves to the PIL Image object
        args = [self.visit(arg) for arg in node.args]
        method = node.method_name

        # A. Support user class attributes and methods (e.g., Aura.intensity or instance.method())
        if hasattr(target, method):
            attr = getattr(target, method)
            if callable(attr):
                args = [self.visit(arg) for arg in node.args] if hasattr(node, 'args') and node.args else []
                return attr(*args)
            else:
                # Returns attribute values directly (e.g., class variables/fields)
                return attr

        # Ensure we are actually operating on a loaded Pillow Image
        if isinstance(target, Image.Image):
            
            # Method 1: .blur(radius)
            if method == "blur":
                radius = args[0] if args else 2
                print(f"[ENGINE] Applying Gaussian blur with radius={radius}...")
                return target.filter(ImageFilter.GaussianBlur(radius))

            # Method 2: .save("output.jpg")
            elif method == "save":
                output_path = args[0]
                target.save(output_path)
                print(f"[ENGINE] Saved modified image to '{output_path}'!")
                return target

            # Method 3: .grayscale()
            elif method == "grayscale":
                print("[ENGINE] Converting to grayscale...")
                return target.convert("L")

            elif method == "resize":
                w, h = args[0], args[1]
                return target.resize((w, h))

            elif method == "rotate":
                angle = args[0]
                return target.rotate(angle, expand=True)

            elif method == "invert":
                # Convert RGB to avoid alpha channel errors on inverts
                return ImageOps.invert(target.convert("RGB"))

            elif method == "brightness":
                factor = args[0] # 1.0 = normal, 0.5 = dark, 2.0 = bright
                enhancer = ImageEnhance.Brightness(target)
                return enhancer.enhance(factor)

            elif method == "pixelate":
                pixel_size = args[0] if args else 10
                # Shrink and blow back up with nearest-neighbor interpolation
                small = target.resize((target.width // pixel_size, target.height // pixel_size), resample=Image.NEAREST)
                return small.resize(target.size, Image.NEAREST)

            elif method == "emboss":
                return target.filter(ImageFilter.EMBOSS)

            elif method == "contour":
                return target.filter(ImageFilter.CONTOUR)
            
            elif method == "text":
                # args: "text string", x, y
                draw_canvas = target.copy()
                draw = ImageDraw.Draw(draw_canvas)
                draw.text((args[1], args[2]), str(args[0]), fill="white")
                return draw_canvas

            elif method == "show":
                target.show()
                return target

            elif method == "edges":
                return target.filter(ImageFilter.FIND_EDGES)

            elif method == "crop":
                left = int(args[0]) if len(args) > 0 else 0
                top = int(args[1]) if len(args) > 1 else 0
                right = int(args[2]) if len(args) > 2 else target.width
                bottom = int(args[3]) if len(args) > 3 else target.height
                return target.crop(left, top, right, bottom)

            elif method == "pad":
                import PIL.ImageOps as ImageOps
                pad_val = int(args[0]) if len(args) > 0 else 10
                color = args[1] if len(args) > 1 else "black"
                if isinstance(color, list): color = tuple(color)
                return ImageOps.expand(target, border=pad_val, fill=color)

            elif method == "canvas":
                w = int(args[0]) if len(args) > 0 else target.width
                h = int(args[1]) if len(args) > 1 else target.height
                color = args[2] if len(args) > 2 else (0, 0, 0, 0) # Transparent default
                if isinstance(color, list): color = tuple(color)
                
                mode = target.mode if target.mode in ["RGB", "RGBA"] else "RGBA"
                new_img = Image.new(mode, (w, h), color)
                # Center the target image on the new canvas
                offset_x = (w - target.width) // 2
                offset_y = (h - target.height) // 2
                new_img.paste(target, (offset_x, offset_y))
                return new_img

            # --- Retro Pop Art & FX ---
            elif method == "posterize":
                bits = int(args[0]) if args else 2 # 1 to 8
                return ImageOps.posterize(target.convert("RGB"), bits)

            elif method == "solarize":
                threshold = int(args[0]) if args else 128
                return ImageOps.solarize(target.convert("RGB"), threshold)

            elif method == "border":
                size = int(args[0]) if args else 10
                color = args[1] if len(args) > 1 else "black"
                return ImageOps.expand(target, border=size, fill=color)

            elif method == "saturate":
                factor = float(args[0])
                return ImageEnhance.Color(target).enhance(factor)

            elif method == "autocontrast":
                return ImageOps.autocontrast(target.convert("RGB"))

            # --- Aspect Ratio & Transformations ---
            elif method == "thumbnail":
                max_dim = int(args[0])
                copy_img = target.copy()
                copy_img.thumbnail((max_dim, max_dim))
                return copy_img

            elif method == "mirror":
                # Flips left side to right side
                flipped = ImageOps.mirror(target)
                width, height = target.size
                left_half = target.crop((0, 0, width // 2, height))
                flipped.paste(left_half, (0, 0))
                return flipped

            # ---------------------------------------------------
            # 1. 3Dialize (Version 3: True Mesh to .OBJ)
            # ---------------------------------------------------
            elif method == "3Dialize" or method == "threeDialize":
                # args: [filename (optional), depth_scale (optional)]
                filename = args[0] if len(args) > 0 else "model.obj"
                depth_scale = float(args[1]) if len(args) > 1 else 50.0
                
                print(f"[ENGINE] Generating 3D Mesh -> {filename}...")
                
                # Convert to height map (grayscale)
                # Resize down slightly so the .obj file doesn't become 5 gigabytes
                max_size = 300 
                mesh_img = target.copy()
                mesh_img.thumbnail((max_size, max_size))
                gray = mesh_img.convert("L")
                
                width, height = gray.size
                pixels = gray.load()

                with open(filename, "w") as f:
                    f.write("# LangArav 3D Mesh Export\n")
                    
                    # 1. Write Vertices (x, y, z=brightness)
                    for y in range(height):
                        for x in range(width):
                            z = (pixels[x, y] / 255.0) * depth_scale
                            # y is negative so the model stands upright in Blender
                            f.write(f"v {x} {-y} {z}\n") 

                    # 2. Write Faces (Connecting the dots into 3D polygons)
                    for y in range(height - 1):
                        for x in range(width - 1):
                            # Calculate vertex indices (OBJ uses 1-based indexing)
                            v1 = y * width + x + 1
                            v2 = v1 + 1
                            v3 = (y + 1) * width + x + 1
                            v4 = v3 + 1
                            # Create a quad face
                            f.write(f"f {v1} {v2} {v4} {v3}\n")
                
                print(f"[ENGINE] 3D Mesh successfully saved to {filename}!")
                return target # Return original image so the script can keep running

            # ---------------------------------------------------
            # 4. Sketch (Color Dodge Pencil Filter)
            # ---------------------------------------------------
            elif method == "sketch":
                gray = target.convert("L")
                inverted = ImageOps.invert(gray)
                # Blur the inverted image
                blurred = inverted.filter(ImageFilter.GaussianBlur(radius=5))
                # Color Dodge blending creates the pencil effect
                return ImageChops.color_dodge(gray, blurred)

            # ---------------------------------------------------
            # 11. Glitch (RGB Channel Shifting)
            # ---------------------------------------------------
            elif method == "glitch":
                shift_amount = int(args[0]) if args else 15
                target = target.convert("RGB")
                r, g, b = target.split()
                
                # Shift Red left, Shift Blue right
                r = ImageChops.offset(r, shift_amount, 0)
                b = ImageChops.offset(b, -shift_amount, 0)
                
                # Recombine with a slight noise aesthetic
                return Image.merge("RGB", (r, g, b))

            # ---------------------------------------------------
            # 20. ASCII Art Generator
            # ---------------------------------------------------
            elif method == "ascii":
                chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
                
                # Shrink image to fit in a console window
                ascii_img = target.copy()
                ascii_img.thumbnail((100, 100))
                gray = ascii_img.convert("L")
                
                pixels = gray.getdata()
                ascii_str = ""
                
                for i, pixel_value in enumerate(pixels):
                    # Map 0-255 brightness to the chars array length
                    char_index = pixel_value * (len(chars) - 1) // 255
                    ascii_str += chars[char_index]
                    
                    # Add newline at the end of every row
                    if (i + 1) % gray.width == 0:
                        ascii_str += "\n"
                
                print("\n[ENGINE] ASCII OUTPUT:\n")
                print(ascii_str)
                return ascii_str

            # ---------------------------------------------------
            # 8. Remove Background (Requires 'rembg')
            # ---------------------------------------------------
            elif method == "removeBackground":
                print("[ENGINE] Using AI to remove background...")
                # Note: 'remove' is imported from rembg at the top
                return remove(target)

            # ---------------------------------------------------
            # 18. Dominant Color (Fast Approximation)
            # ---------------------------------------------------
            elif method == "dominantColor":
                # Converts image to RGB, finds the median color of all pixels
                median_color = ImageStat.Stat(target.convert("RGB")).median
                rgb_tuple = tuple(median_color)
                print(f"[ENGINE] Dominant Color: {rgb_tuple}")
                return rgb_tuple

            elif method == "mosaic":
                tiles = int(args[0]) if args else 100
                # Calculate height to maintain aspect ratio
                ratio = target.height / target.width
                small = target.resize((tiles, int(tiles * ratio)), resample=Image.NEAREST)
                return small.resize(target.size, resample=Image.NEAREST)

            elif method == "pixelSort":
                print("[ENGINE] Sorting pixels...")
                # Convert to numpy array
                arr = np.array(target.convert("RGB"))
                # Sort the pixels along the x-axis (rows) to create a smeared, glitchy modern art look
                arr.sort(axis=1) 
                return Image.fromarray(arr)

            elif method == "vaporwave":
                # Convert to grayscale, then map darks to blue/purple and lights to hot pink
                gray = target.convert("L")
                vapor = ImageOps.colorize(gray, black="#1a0033", white="#ff00ff")
                # Add a soft bloom/blur overlay
                bloom = vapor.filter(ImageFilter.GaussianBlur(10))
                return Image.blend(vapor, bloom, 0.4)

            elif method == "neon":
                # Find edges and colorize them cyan
                edges = target.filter(ImageFilter.FIND_EDGES).convert("L")
                neon_base = ImageOps.colorize(edges, black="black", white="#00ffff")
                # Create the glow by blurring the edges and adding it back on top
                glow = neon_base.filter(ImageFilter.GaussianBlur(5))
                from PIL import ImageChops
                return ImageChops.add(neon_base, glow)

            elif method == "hologram":
                # Blue tint + scanlines + transparency
                holo = ImageOps.colorize(target.convert("L"), black="#001133", white="#00ffff")
                draw = ImageDraw.Draw(holo)
                # Draw scanlines
                for y in range(0, holo.height, 4):
                    draw.line([(0, y), (holo.width, y)], fill=(0, 255, 255), width=1)
                # Make it semi-transparent
                holo.putalpha(180)
                return holo

            elif method == "kaleidoscope":
                # Mirrors the top-left quadrant into all 4 corners
                w, h = target.size
                quad = target.crop((0, 0, w // 2, h // 2))
                canvas = Image.new("RGB", (w, h))
                canvas.paste(quad, (0, 0))
                canvas.paste(ImageOps.mirror(quad), (w // 2, 0))
                canvas.paste(ImageOps.flip(quad), (0, h // 2))
                canvas.paste(ImageOps.mirror(ImageOps.flip(quad)), (w // 2, h // 2))
                return canvas

            # ==========================================
            # GROUP 2: PAINTING & CARTOONS (using OpenCV & Pillow)
            # ==========================================
            elif method == "cartoon":
                level = int(args[0]) if args else 3
                print(f"[ENGINE] Cartoonifying at level {level}...")
                cv_img = np.array(target.convert("RGB"))[:, :, ::-1].copy() # Convert PIL to cv2 BGR
                # 1. Bilateral Filter for smooth color palette
                color = cv2.bilateralFilter(cv_img, 9, 250, 250)
                # 2. Edge detection
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, level)
                # 3. Blend
                cartoon = cv2.bitwise_and(color, color, mask=edges)
                return Image.fromarray(cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB))

            elif method == "watercolor":
                print("[ENGINE] Applying Watercolor effect...")
                # Smooth heavily, then enhance edges
                base = target.filter(ImageFilter.ModeFilter(size=9))
                return base.filter(ImageFilter.EDGE_ENHANCE_MORE)

            elif method == "oilpaint":
                print("[ENGINE] Applying Oil Paint effect...")
                # Simulates strokes by applying rank filters
                return target.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))

            # ==========================================
            # GROUP 3: DATA & ANALYSIS
            # ==========================================
            elif method == "histogram":
                hist = target.histogram()
                # Pillow returns a flat list of 768 integers (256 for R, 256 for G, 256 for B)
                red = hist[0:256]
                green = hist[256:512]
                blue = hist[512:768]
                # Return it as a Python dictionary so LangArav can use it!
                result = {"Red": red, "Green": green, "Blue": blue}
                print("[ENGINE] Histogram calculated.")
                return result

            elif method == "palette":
                num_colors = int(args[0]) if args else 10
                # Quantizes the image down to K colors and extracts the palette
                quantized = target.convert("P", palette=Image.ADAPTIVE, colors=num_colors)
                pal = quantized.getpalette()[:num_colors*3]
                # Chunk into RGB tuples
                dominant_colors = [tuple(pal[i:i+3]) for i in range(0, len(pal), 3)]
                print(f"[ENGINE] Top {num_colors} Colors: {dominant_colors}")
                return dominant_colors

            elif method == "aiUpscale":
                print("[ENGINE] AI Upscale (Currently using Lanczos bicubic approximation)...")
                # Double the size using the highest quality resampling until ESRGAN is added
                return target.resize((target.width * 2, target.height * 2), Image.LANCZOS)

            elif method == "detect":
                obj_type = str(args[0]).lower() if args else "face"
                print(f"[ENGINE - AI] Running detection for: '{obj_type}'...")
    
                # 1. Convert Pillow Image to OpenCV format (BGR numpy array)
                cv_img = np.array(target.convert("RGB"))[:, :, ::-1].copy()
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

                # 2. Select standard OpenCV classifier cascade
                if "face" in obj_type:
                    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                elif "eye" in obj_type:
                    cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
                elif "car" in obj_type or "vehicle" in obj_type:
                    cascade_path = cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml'
                else:
                    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

                detector = cv2.CascadeClassifier(cascade_path)
    
                # 3. Detect bounding boxes (x, y, width, height)
                boxes = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                print(f"[ENGINE - AI] Found {len(boxes)} '{obj_type}' instance(s)!")

                # 4. Draw vibrant cyan bounding boxes around detected items
                for (x, y, w, h) in boxes:
                    cv2.rectangle(cv_img, (x, y), (x + w, y + h), (255, 255, 0), 3)

                # 5. Convert back to Pillow Image
                return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

            elif method == "lens":
                strength = float(args[0]) if args else 0.5
                print(f"[ENGINE - GEOMETRY] Applying Fish-Eye lens distortion (strength={strength})...")
    
                w, h = target.size
                cx, cy = w / 2, h / 2
    
                # Generate coordinate grids
                x, y = np.meshgrid(np.arange(w), np.arange(h))
                x_norm = (x - cx) / cx
                y_norm = (y - cy) / cy
                r = np.sqrt(x_norm**2 + y_norm**2)
    
                # Radial distortion formula
                factor = 1 + strength * r**2
                map_x = (x_norm * factor * cx + cx).astype(np.float32)
                map_y = (y_norm * factor * cy + cy).astype(np.float32)

                cv_img = np.array(target.convert("RGB"))
                distorted = cv2.remap(cv_img, map_x, map_y, interpolation=cv2.INTER_LINEAR)
                return Image.fromarray(distorted)

            elif method == "sphere":
                print("[ENGINE - GEOMETRY] Mapping image onto a 3D Sphere...")
                w, h = target.size
                cx, cy = w / 2, h / 2
                radius = min(cx, cy)
    
                x, y = np.meshgrid(np.arange(w), np.arange(h))
                dx, dy = (x - cx) / radius, (y - cy) / radius
                r = np.sqrt(dx**2 + dy**2)
    
                # Sphere displacement formula
                mask = r <= 1.0
                z = np.sqrt(np.maximum(0, 1.0 - r**2))
    
                map_x = np.where(mask, cx + (dx / (z + 0.001)) * (radius / 2), x).astype(np.float32)
                map_y = np.where(mask, cy + (dy / (z + 0.001)) * (radius / 2), y).astype(np.float32)

                cv_img = np.array(target.convert("RGB"))
                spherized = cv2.remap(cv_img, map_x, map_y, cv2.INTER_LINEAR)
                return Image.fromarray(spherized)

            elif method == "restore":
                h_strength = int(args[0]) if args else 10
                print(f"[ENGINE - AI] Running Non-Local Means AI Denoising (strength={h_strength})...")
    
                cv_img = np.array(target.convert("RGB"))[:, :, ::-1]
                # Restores noisy photos while preserving sharp edges
                restored = cv2.fastNlMeansDenoisingColored(cv_img, None, h_strength, h_strength, 7, 21)
    
                return Image.fromarray(cv2.cvtColor(restored, cv2.COLOR_BGR2RGB))

            elif method == "objectErase":
                obj_type = str(args[0]).lower() if args else "face"
                print(f"[ENGINE - AI] Detecting and erasing '{obj_type}'...")

                cv_img = np.array(target.convert("RGB"))[:, :, ::-1].copy()
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

                # 1. Detect target object to erase
                cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                boxes = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

                if len(boxes) == 0:
                    print(f"[ENGINE - AI] No '{obj_type}' found to erase.")
                    return target

                # 2. Create binary mask over detected regions
                mask = np.zeros(gray.shape, dtype=np.uint8)
                for (x, y, w, h) in boxes:
                    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

                # 3. Inpaint background into masked areas
                inpainted = cv2.inpaint(cv_img, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)

                return Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))

            elif method == "superResolution":
                scale_factor = int(args[0]) if args else 2
                print(f"[ENGINE - AI] Booting Super Resolution Engine ({scale_factor}x)...")

                # If DNN models aren't present locally, fall back gracefully to Lanczos resampling
                try:
                    sr = cv2.dnn_superres.DnnSuperResImpl_create()
                    # Path to pre-trained model file (e.g., FSRCNN_x2.pb)
                    sr.readModel(f"FSRCNN_x{scale_factor}.pb")
                    sr.setModel("fsrcnn", scale_factor)

                    cv_img = np.array(target.convert("RGB"))[:, :, ::-1]
                    upscaled = sr.upsample(cv_img)
                    return Image.fromarray(cv2.cvtColor(upscaled, cv2.COLOR_BGR2RGB))
                except Exception as e:
                    print("[ENGINE - AI] Local DNN weights not found. Falling back to high-grade Lanczos upscaler...")
                    return target.resize((target.width * scale_factor, target.height * scale_factor), Image.LANCZOS)

            elif method == "average":
                other_img = args[0]
                if isinstance(other_img, Image.Image):
                    arr1 = np.array(target.convert("RGB"))
                    arr2 = np.array(other_img.convert("RGB"))
                    
                    if arr1.shape != arr2.shape:
                        arr2 = cv2.resize(arr2, (arr1.shape[1], arr1.shape[0]))
                    
                    # Blends 50% of image 1 and 50% of image 2
                    avg_arr = cv2.addWeighted(arr1, 0.5, arr2, 0.5, 0)
                    return Image.fromarray(avg_arr)
                else:
                    raise TypeError("Method 'average()' requires another image argument.")

            # ==========================================
            # GROUP 5: ADVANCED MATHEMATICAL TRANSFORMS
            # ==========================================
            
            # 1. Discrete Cosine Transform (DCT)
            elif method == "dct":
                gray = cv2.cvtColor(np.array(target.convert("RGB")), cv2.COLOR_RGB2GRAY).astype(np.float32)
                dct_img = cv2.dct(gray)
                # Normalize frequency spectrum for clean viewing
                dct_vis = np.uint8(np.absolute(dct_img) / np.max(np.abs(dct_img)) * 255)
                return Image.fromarray(dct_vis)

            # 2. Wavelet Transform (DWT using PyWavelets)
            elif method == "wavelet" or method == "dwt":
                import pywt
                gray = cv2.cvtColor(np.array(target.convert("RGB")), cv2.COLOR_RGB2GRAY)
                coeffs2 = pywt.dwt2(gray, 'haar')
                LL, (LH, HL, HH) = coeffs2
                # Return approximation coefficients visualization
                return Image.fromarray(np.uint8(np.abs(LL)))

            # 3. Morphology (Dilate, Erode, Open, Close)
            elif method in ["dilate", "erode", "open", "close"]:
                kernel_size = int(args[0]) if args else 3
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
                cv_img = np.array(target.convert("RGB"))
                
                if method == "dilate":
                    res = cv2.dilate(cv_img, kernel, iterations=1)
                elif method == "erode":
                    res = cv2.erode(cv_img, kernel, iterations=1)
                elif method == "open":
                    res = cv2.morphologyEx(cv_img, cv2.MORPH_OPEN, kernel)
                elif method == "close":
                    res = cv2.morphologyEx(cv_img, cv2.MORPH_CLOSE, kernel)
                return Image.fromarray(res)

            # 4. Affine Transforms (Rotation, Translation, Shear matrix)
            elif method == "affine":
                angle = float(args[0]) if len(args) > 0 else 0
                tx = float(args[1]) if len(args) > 1 else 0
                ty = float(args[2]) if len(args) > 2 else 0
                h, w = target.height, target.width
                
                rad = np.radians(angle)
                M = np.float32([[np.cos(rad), -np.sin(rad), tx],
                                [np.sin(rad), np.cos(rad), ty]])
                cv_img = np.array(target.convert("RGB"))
                res = cv2.warpAffine(cv_img, M, (w, h))
                return Image.fromarray(res)

            # 5. Perspective Transforms (4-point corner skewing)
            elif method == "perspective":
                h, w = target.height, target.width
                src_pts = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
                dx = float(args[0]) if len(args) > 0 else 40
                dst_pts = np.float32([[dx, dx], [w - dx, 0], [0, h], [w, h - dx]])
                
                M = cv2.getPerspectiveTransform(src_pts, dst_pts)
                cv_img = np.array(target.convert("RGB"))
                res = cv2.warpPerspective(cv_img, M, (w, h))
                return Image.fromarray(res)

            # 6. Polar Transforms (Cartesian to Polar mapping)
            elif method == "polar":
                cv_img = np.array(target.convert("RGB"))
                h, w = cv_img.shape[:2]
                center = (w / 2, h / 2)
                max_radius = np.sqrt(center[0]**2 + center[1]**2)
                polar_img = cv2.warpPolar(cv_img, (w, h), center, max_radius, cv2.WARP_POLAR_LINEAR)
                return Image.fromarray(polar_img)

            # 7. Frequency Filters (FFT Low-pass & High-pass)
            elif method == "freqFilter" or method == "fftFilter":
                filter_type = str(args[0]).lower() if len(args) > 0 else "lowpass"
                cutoff = int(args[1]) if len(args) > 1 else 30
                
                gray = cv2.cvtColor(np.array(target.convert("RGB")), cv2.COLOR_RGB2GRAY)
                f = np.fft.fft2(gray)
                fshift = np.fft.fftshift(f)
                
                rows, cols = gray.shape
                crow, ccol = rows // 2, cols // 2
                mask = np.ones((rows, cols), np.uint8)
                
                if filter_type == "lowpass":
                    mask[...] = 0
                    cv2.circle(mask, (ccol, crow), cutoff, 1, -1)
                elif filter_type == "highpass":
                    cv2.circle(mask, (ccol, crow), cutoff, 0, -1)
                    
                fshift_filtered = fshift * mask
                f_ishift = np.fft.ifftshift(fshift_filtered)
                img_back = np.abs(np.fft.ifft2(f_ishift))
                img_back = np.uint8(np.clip(img_back, 0, 255))
                return Image.fromarray(cv2.cvtColor(img_back, cv2.COLOR_GRAY2RGB))

            # 8. Convolution Kernels (Sharpen, Edge, Box, Custom)
            elif method == "convolve":
                kernel_name = args[0] if len(args) > 0 else "sharpen"
                
                if kernel_name == "sharpen":
                    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                elif kernel_name == "edge":
                    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
                elif kernel_name == "box":
                    kernel = np.ones((3, 3), np.float32) / 9.0
                elif isinstance(kernel_name, list):
                    kernel = np.array(kernel_name, dtype=np.float32)
                else:
                    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                    
                cv_img = np.array(target.convert("RGB"))
                filtered = cv2.filter2D(cv_img, -1, kernel)
                return Image.fromarray(filtered)

            # ==========================================
            # 9. THE .graph() EQUATION PLOTTING METHOD
            # ==========================================
            elif method == "graph":
                # Syntax: img.graph("x**2", "cyan", 3)
                expr = str(args[0]) if len(args) > 0 else "x"
                color_arg = args[1] if len(args) > 1 else "cyan"
                thickness = int(args[2]) if len(args) > 2 else 2
                
                # Resolve color names to BGR tuples
                color_map = {
                    "red": (0, 0, 255), "green": (0, 255, 0), "blue": (255, 0, 0),
                    "cyan": (255, 255, 0), "yellow": (0, 255, 255), "magenta": (255, 0, 255),
                    "white": (255, 255, 255), "orange": (0, 165, 255)
                }
                bgr_color = color_map.get(color_arg.lower(), (0, 255, 255)) if isinstance(color_arg, str) else color_arg

                cv_img = np.array(target.convert("RGB"))[:, :, ::-1].copy()
                h, w = cv_img.shape[:2]
                
                # Center coordinate system origin at image center
                cx, cy = w / 2, h / 2
                scale = 20.0 # Pixels per mathematical unit
                
                points = []
                for px in range(w):
                    x = (px - cx) / scale
                    try:
                        safe_dict = {
                    "x": x,
                    "np": np,
                    
                    # --- Mathematical Constants ---
                    "pi": np.pi,
                    "e": np.e,
                    "tau": np.tau,
                    "inf": np.inf,
                    "nan": np.nan,
                    
                    # --- Trigonometric Functions ---
                    "sin": np.sin,
                    "cos": np.cos,
                    "tan": np.tan,
                    "arcsin": np.arcsin,
                    "arccos": np.arccos,
                    "arctan": np.arctan,
                    "arctan2": np.arctan2,
                    "hypot": np.hypot,
                    
                    # --- Hyperbolic Functions ---
                    "sinh": np.sinh,
                    "cosh": np.cosh,
                    "tanh": np.tanh,
                    "arcsinh": np.arcsinh,
                    "arccosh": np.arccosh,
                    "arctanh": np.arctanh,
                    
                    # --- Exponentials & Logarithms ---
                    "exp": np.exp,
                    "expm1": np.expm1,
                    "exp2": np.exp2,
                    "log": np.log,
                    "log2": np.log2,
                    "log10": np.log10,
                    "log1p": np.log1p,
                    "power": np.power,
                    "sqrt": np.sqrt,
                    "cbrt": np.cbrt,
                    "square": np.square,
                    
                    # --- Arithmetic & Rounding ---
                    "abs": np.abs,
                    "fabs": np.fabs,
                    "ceil": np.ceil,
                    "floor": np.floor,
                    "trunc": np.trunc,
                    "round": np.round,
                    "sign": np.sign,
                    "maximum": np.maximum,
                    "minimum": np.minimum,
                    "mod": np.mod,
                    "remainder": np.remainder,
                    "fmod": np.fmod,
                    "sinc": np.sinc,
                    
                    # --- Angle Conversions ---
                    "degrees": np.degrees,
                    "radians": np.radians,
                    
                    # --- Safe Python Built-ins ---
                    "min": min,
                    "max": max,
                    "pow": pow
                }
                        # Safely evaluate math expression string
                        y = eval(expr, {"__builtins__": {}}, safe_dict)
                        
                        if isinstance(y, (int, float, np.number)) and not np.isnan(y) and not np.isinf(y):
                            py = int(cy - (y * scale))
                            if -h <= py < h * 2: # Keep within plotting space
                                points.append((px, py))
                    except Exception:
                        continue
                
                if len(points) > 1:
                    pts_array = np.array(points, np.int32).reshape((-1, 1, 2))
                    cv2.polylines(cv_img, [pts_array], isClosed=False, color=bgr_color, thickness=thickness)
                    
                return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

            # ==========================================
            # GROUP 6: COLOR SCIENCE & CONVERSIONS
            # ==========================================

            # 1. Color Space Conversions (HSV, LAB, YUV, XYZ)
            elif method in ["hsv", "lab", "yuv", "xyz"]:
                rgb = np.array(target.convert("RGB"))
                if method == "hsv":
                    converted = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
                elif method == "lab":
                    converted = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
                elif method == "yuv":
                    converted = cv2.cvtColor(rgb, cv2.COLOR_RGB2YUV)
                elif method == "xyz":
                    converted = cv2.cvtColor(rgb, cv2.COLOR_RGB2XYZ)
                return Image.fromarray(converted)

            # 2. Gamma Correction (I_out = I_in ^ (1 / gamma))
            elif method == "gamma":
                gamma_val = float(args[0]) if args else 2.2
                inv_gamma = 1.0 / max(gamma_val, 0.001)
                # Build lookup table for speed
                table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
                rgb = np.array(target.convert("RGB"))
                return Image.fromarray(cv2.LUT(rgb, table))

            # 3. Linear RGB Transformation
            elif method == "linearRGB":
                arr = np.array(target.convert("RGB")).astype(np.float32) / 255.0
                # sRGB to Linear conversion formula
                linear = np.where(arr <= 0.04045, arr / 12.92, ((arr + 0.055) / 1.055) ** 2.4)
                return Image.fromarray((linear * 255.0).clip(0, 255).astype(np.uint8))

            # 4. Exposure Adjustment (in EV stops: I_out = I_in * 2^EV)
            elif method == "exposure":
                ev = float(args[0]) if args else 1.0
                scale = 2.0 ** ev
                arr = np.array(target.convert("RGB")).astype(np.float32) * scale
                return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

            # 5. Color Temperature Adjustment (Warmth / Coolness)
            elif method == "temperature":
                # temp > 0 warms (adds Red, drops Blue), temp < 0 cools
                temp = float(args[0]) if args else 20.0
                arr = np.array(target.convert("RGB")).astype(np.float32)
                arr[:, :, 0] += temp   # Red channel
                arr[:, :, 2] -= temp   # Blue channel
                return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

            # 6. Tint Adjustment (Green / Magenta shift)
            elif method == "tint":
                # tint > 0 adds Magenta (drops Green), tint < 0 adds Green
                t_val = float(args[0]) if args else 20.0
                arr = np.array(target.convert("RGB")).astype(np.float32)
                arr[:, :, 1] -= t_val   # Green channel
                return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

            # 7. Gray-World Auto White Balance
            elif method == "whiteBalance":
                rgb = np.array(target.convert("RGB")).astype(np.float32)
                avg_r, avg_g, avg_b = np.mean(rgb[:, :, 0]), np.mean(rgb[:, :, 1]), np.mean(rgb[:, :, 2])
                avg_gray = (avg_r + avg_g + avg_b) / 3.0
                
                rgb[:, :, 0] *= (avg_gray / max(avg_r, 1e-5))
                rgb[:, :, 1] *= (avg_gray / max(avg_g, 1e-5))
                rgb[:, :, 2] *= (avg_gray / max(avg_b, 1e-5))
                return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))

            # 8. Standard Global Histogram Equalization
            elif method == "histogramEqualization":
                # Equalize on the Y channel in YUV space to preserve original colors
                yuv = cv2.cvtColor(np.array(target.convert("RGB")), cv2.COLOR_RGB2YUV)
                yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
                res = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
                return Image.fromarray(res)

            # 9. CLAHE (Contrast Limited Adaptive Histogram Equalization)
            elif method == "CLAHE" or method == "clahe":
                clip_limit = float(args[0]) if args else 2.0
                tile_grid = int(args[1]) if len(args) > 1 else 8
                
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid, tile_grid))
                lab = cv2.cvtColor(np.array(target.convert("RGB")), cv2.COLOR_RGB2LAB)
                lab[:, :, 0] = clahe.apply(lab[:, :, 0]) # Apply to L (Lightness) channel
                res = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
                return Image.fromarray(res)

            # 10. Reinhard Filmic Tone Mapping
            elif method == "toneMap":
                intensity = float(args[0]) if args else 1.0
                arr = np.array(target.convert("RGB")).astype(np.float32) / 255.0
                
                # Filmic Reinhard equation: I_mapped = I / (1 + I)
                mapped = (arr * intensity) / (1.0 + (arr * intensity))
                return Image.fromarray((mapped * 255.0).clip(0, 255).astype(np.uint8))

            # ==========================================
            # GROUP 7: MASKING & SELECTION TOOLS
            # ==========================================

            # 1. Mask (Cut out or apply transparency using a grayscale mask)
            elif method == "mask":
                mask_arg = args[0]
                if isinstance(mask_arg, Image.Image):
                    mask_img = mask_arg.convert("L")
                    if mask_img.size != target.size:
                        mask_img = mask_img.resize(target.size)
                    
                    res = target.convert("RGBA")
                    res.putalpha(mask_img)
                    return res
                else:
                    raise TypeError("Method 'mask()' requires an Image object as mask.")

            # 2. Thresholding (Manual intensity cutoff or Otsu Auto-Threshold)
            elif method == "threshold":
                cutoff = args[0] if len(args) > 0 else 128
                gray = cv2.cvtColor(np.array(target.convert("RGB")), cv2.COLOR_RGB2GRAY)
                
                if str(cutoff).lower() == "otsu":
                    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                else:
                    val = int(cutoff)
                    _, thresh = cv2.threshold(gray, val, 255, cv2.THRESH_BINARY)
                return Image.fromarray(thresh)

            # 3. Magic Select (Photoshop Magic Wand Tool)
            elif method == "magicSelect":
                # args: x, y, tolerance (default 32)
                x = int(args[0]) if len(args) > 0 else target.width // 2
                y = int(args[1]) if len(args) > 1 else target.height // 2
                tol = int(args[2]) if len(args) > 2 else 32

                cv_img = cv2.cvtColor(np.array(target.convert("RGB")), cv2.COLOR_RGB2BGR)
                h, w = cv_img.shape[:2]

                ff_mask = np.zeros((h + 2, w + 2), np.uint8)
                flags = 4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY

                cv2.floodFill(cv_img, ff_mask, (x, y), 0, (tol, tol, tol), (tol, tol, tol), flags)
                
                selection_mask = ff_mask[1:h+1, 1:w+1]
                return Image.fromarray(selection_mask)

            # 4. Polygon Mask Generator
            elif method == "polygonMask":
                # args: points e.g. [[x1, y1], [x2, y2], ...] or flat list [x1, y1, x2, y2, ...]
                pts = args[0] if len(args) > 0 else []
                
                mask = Image.new("L", target.size, 0)
                draw = ImageDraw.Draw(mask)
                
                if pts:
                    if isinstance(pts[0], (list, tuple)):
                        poly_points = [tuple(p) for p in pts]
                    else:
                        poly_points = [(pts[i], pts[i+1]) for i in range(0, len(pts), 2)]
                    
                    draw.polygon(poly_points, fill=255)
                return mask

            # 5. Flood Fill (Paint Bucket Tool)
            elif method == "floodFill":
                # args: x, y, color (e.g. "red" or (255,0,0)), tolerance (default 32)
                x = int(args[0]) if len(args) > 0 else 0
                y = int(args[1]) if len(args) > 1 else 0
                color_arg = args[2] if len(args) > 2 else "red"
                tol = int(args[3]) if len(args) > 3 else 32

                if isinstance(color_arg, str):
                    from PIL import ImageColor
                    fill_rgb = ImageColor.getrgb(color_arg)
                elif isinstance(color_arg, (list, tuple)):
                    fill_rgb = tuple(color_arg[:3])
                else:
                    fill_rgb = (255, 0, 0)

                fill_bgr = (fill_rgb[2], fill_rgb[1], fill_rgb[0])
                cv_img = cv2.cvtColor(np.array(target.convert("RGB")), cv2.COLOR_RGB2BGR)
                
                h, w = cv_img.shape[:2]
                mask = np.zeros((h + 2, w + 2), np.uint8)
                
                cv2.floodFill(cv_img, mask, (x, y), fill_bgr, (tol, tol, tol), (tol, tol, tol), cv2.FLOODFILL_FIXED_RANGE)
                return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

            # 6. Alpha Mask (Set alpha channel directly)
            elif method == "alphaMask":
                mask_arg = args[0]
                if isinstance(mask_arg, Image.Image):
                    alpha_channel = mask_arg.convert("L")
                    if alpha_channel.size != target.size:
                        alpha_channel = alpha_channel.resize(target.size)
                    
                    rgba = target.convert("RGBA")
                    rgba.putalpha(alpha_channel)
                    return rgba
                else:
                    raise TypeError("Method 'alphaMask()' requires an Image object.")

            # 7. Clip Pixel Intensities
            elif method == "clip":
                min_val = float(args[0]) if len(args) > 0 else 0
                max_val = float(args[1]) if len(args) > 1 else 255
                
                arr = np.array(target.convert("RGB"))
                clipped = np.clip(arr, min_val, max_val).astype(np.uint8)
                return Image.fromarray(clipped)

            elif method == "warp":
                # args[0]: [[x,y], [x,y], [x,y], [x,y]] source pts
                # args[1]: [[x,y], [x,y], [x,y], [x,y]] dest pts
                pts1 = np.float32(args[0])
                pts2 = np.float32(args[1])
                cv_img = cv2.cvtColor(np.array(target.convert("RGB")), cv2.COLOR_RGB2BGR)
                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                res = cv2.warpPerspective(cv_img, matrix, (target.width, target.height))
                return Image.fromarray(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))

            # 9. Mesh Warp (Flag/Ripple sine wave distortion)
            elif method == "meshWarp":
                amp = float(args[0]) if len(args) > 0 else 10.0
                freq = float(args[1]) if len(args) > 1 else 0.05
                cv_img = np.array(target.convert("RGB"))
                h, w = cv_img.shape[:2]
                
                map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
                map_x = map_x.astype(np.float32) + amp * np.sin(map_y.astype(np.float32) * freq)
                map_y = map_y.astype(np.float32)
                
                res = cv2.remap(cv_img, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
                return Image.fromarray(res)

            # 10. Liquify (Local vector push/smudge)
            elif method == "liquify":
                # args: cx, cy, push_x, push_y, radius
                cx, cy = float(args[0]), float(args[1])
                dx, dy = float(args[2]), float(args[3])
                radius = float(args[4]) if len(args) > 4 else 100.0
                
                cv_img = np.array(target.convert("RGB"))
                h, w = cv_img.shape[:2]
                map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
                map_x, map_y = map_x.astype(np.float32), map_y.astype(np.float32)
                
                dist_sq = (map_x - cx)**2 + (map_y - cy)**2
                mask = dist_sq < radius**2
                
                # Smooth falloff bell curve
                falloff = (1.0 - dist_sq[mask] / (radius**2))**2
                
                # Fetch pixels from the opposite direction to push image forward
                map_x[mask] -= dx * falloff
                map_y[mask] -= dy * falloff
                
                res = cv2.remap(cv_img, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
                return Image.fromarray(res)

            # 11. Swirl (Vortex rotation)
            elif method == "swirl":
                strength = float(args[0]) if len(args) > 0 else 2.0 
                radius = float(args[1]) if len(args) > 1 else min(target.width, target.height) / 2
                cx = float(args[2]) if len(args) > 2 else target.width / 2
                cy = float(args[3]) if len(args) > 3 else target.height / 2
                
                cv_img = np.array(target.convert("RGB"))
                h, w = cv_img.shape[:2]
                map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
                map_x, map_y = map_x.astype(np.float32) - cx, map_y.astype(np.float32) - cy
                
                r = np.sqrt(map_x**2 + map_y**2)
                theta = np.arctan2(map_y, map_x)
                
                # Apply rotation strongest at center, fading out to radius
                falloff = np.maximum(0, 1 - (r / radius))
                theta += strength * falloff
                
                map_x = cx + r * np.cos(theta)
                map_y = cy + r * np.sin(theta)
                
                res = cv2.remap(cv_img, map_x.astype(np.float32), map_y.astype(np.float32), interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
                return Image.fromarray(res)

            # ==========================================
            # GEOMETRY & DISTORTIONS
            # ==========================================
            elif method == "pinch":
                amount = float(args[0]) if args else 0.5
                radius = float(args[1]) if len(args) > 1 else min(target.width, target.height) / 2
                print(f"[ENGINE - GEOMETRY] Applying Pinch distortion (amount={amount}, radius={radius})...")
                
                w, h = target.size
                cx, cy = w / 2, h / 2
                x, y = np.meshgrid(np.arange(w), np.arange(h))
                
                dx, dy = x - cx, y - cy
                r = np.sqrt(dx**2 + dy**2)
                
                mask = r < radius
                # To pinch, we pull pixels from further out (exponent > 0)
                factor = np.ones_like(r)
                factor[mask] = (r[mask] / radius) ** amount
                
                map_x = np.where(mask, cx + dx * factor, x).astype(np.float32)
                map_y = np.where(mask, cy + dy * factor, y).astype(np.float32)
                
                cv_img = np.array(target.convert("RGB"))
                pinched = cv2.remap(cv_img, map_x, map_y, cv2.INTER_LINEAR)
                return Image.fromarray(pinched)

            elif method == "bulge":
                amount = float(args[0]) if args else 0.5
                radius = float(args[1]) if len(args) > 1 else min(target.width, target.height) / 2
                print(f"[ENGINE - GEOMETRY] Applying Bulge distortion (amount={amount}, radius={radius})...")
                
                w, h = target.size
                cx, cy = w / 2, h / 2
                x, y = np.meshgrid(np.arange(w), np.arange(h))
                
                dx, dy = x - cx, y - cy
                r = np.sqrt(dx**2 + dy**2)
                
                mask = r < radius
                # To bulge, we push pixels outwards by fetching from closer to center
                factor = np.ones_like(r)
                # Ensure we don't divide by zero or invert the image mathematically
                p = 1.0 - (0.5 * min(abs(amount), 1.0))
                factor[mask] = (r[mask] / radius) ** (p - 1)
                
                map_x = np.where(mask, cx + dx * factor, x).astype(np.float32)
                map_y = np.where(mask, cy + dy * factor, y).astype(np.float32)
                
                cv_img = np.array(target.convert("RGB"))
                bulged = cv2.remap(cv_img, map_x, map_y, cv2.INTER_LINEAR)
                return Image.fromarray(bulged)


            # ==========================================
            # FREQUENCY DOMAIN (FFT Filters applied end-to-end)
            # ==========================================
            elif method == "bandpass":
                low_cutoff = int(args[0]) if args else 10
                high_cutoff = int(args[1]) if len(args) > 1 else 50
                print(f"[ENGINE - FREQUENCY] Applying Bandpass Filter (low={low_cutoff}, high={high_cutoff})...")
                
                gray = np.array(target.convert("L"))
                fshift = np.fft.fftshift(np.fft.fft2(gray))
                
                rows, cols = gray.shape
                crow, ccol = rows // 2, cols // 2
                y, x = np.ogrid[:rows, :cols]
                dist = np.sqrt((x - ccol)**2 + (y - crow)**2)
                
                mask = (dist >= low_cutoff) & (dist <= high_cutoff)
                fshift_filtered = fshift * mask
                
                img_back = np.abs(np.fft.ifft2(np.fft.ifftshift(fshift_filtered)))
                return Image.fromarray(np.clip(img_back, 0, 255).astype(np.uint8))

            elif method == "bandstop":
                low_cutoff = int(args[0]) if args else 10
                high_cutoff = int(args[1]) if len(args) > 1 else 50
                print(f"[ENGINE - FREQUENCY] Applying Bandstop Filter (low={low_cutoff}, high={high_cutoff})...")
                
                gray = np.array(target.convert("L"))
                fshift = np.fft.fftshift(np.fft.fft2(gray))
                
                rows, cols = gray.shape
                crow, ccol = rows // 2, cols // 2
                y, x = np.ogrid[:rows, :cols]
                dist = np.sqrt((x - ccol)**2 + (y - crow)**2)
                
                mask = ~((dist >= low_cutoff) & (dist <= high_cutoff))
                fshift_filtered = fshift * mask
                
                img_back = np.abs(np.fft.ifft2(np.fft.ifftshift(fshift_filtered)))
                return Image.fromarray(np.clip(img_back, 0, 255).astype(np.uint8))

            elif method == "notch":
                u = int(args[0]) if args else 30
                v = int(args[1]) if len(args) > 1 else 30
                r = int(args[2]) if len(args) > 2 else 5
                print(f"[ENGINE - FREQUENCY] Applying Notch Filter at ({u}, {v}) radius={r}...")
                
                gray = np.array(target.convert("L"))
                fshift = np.fft.fftshift(np.fft.fft2(gray))
                
                rows, cols = gray.shape
                crow, ccol = rows // 2, cols // 2
                y, x = np.ogrid[:rows, :cols]
                
                mask = np.ones((rows, cols), np.uint8)
                dist1 = np.sqrt((x - (ccol + u))**2 + (y - (crow + v))**2)
                dist2 = np.sqrt((x - (ccol - u))**2 + (y - (crow - v))**2)
                
                mask[dist1 <= r] = 0
                mask[dist2 <= r] = 0
                
                fshift_filtered = fshift * mask
                img_back = np.abs(np.fft.ifft2(np.fft.ifftshift(fshift_filtered)))
                return Image.fromarray(np.clip(img_back, 0, 255).astype(np.uint8))

            elif method == "frequencyMask":
                mask_arg = args[0]
                print("[ENGINE - FREQUENCY] Multiplying custom mask in Frequency Domain...")
                if isinstance(mask_arg, Image.Image):
                    gray = np.array(target.convert("L"))
                    mask_img = np.array(mask_arg.convert("L").resize(target.size)) / 255.0
                    
                    fshift = np.fft.fftshift(np.fft.fft2(gray))
                    fshift_filtered = fshift * mask_img
                    
                    img_back = np.abs(np.fft.ifft2(np.fft.ifftshift(fshift_filtered)))
                    return Image.fromarray(np.clip(img_back, 0, 255).astype(np.uint8))
                else:
                    raise TypeError("frequencyMask requires an Image object as a mask.")

            elif method == "magnitude":
                print("[ENGINE - FREQUENCY] Rendering FFT Magnitude Spectrum...")
                gray = np.array(target.convert("L"))
                fshift = np.fft.fftshift(np.fft.fft2(gray))
                
                magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
                magnitude_spectrum = np.clip(magnitude_spectrum, 0, 255).astype(np.uint8)
                return Image.fromarray(magnitude_spectrum)

            elif method == "phase":
                print("[ENGINE - FREQUENCY] Rendering FFT Phase Spectrum...")
                gray = np.array(target.convert("L"))
                fshift = np.fft.fftshift(np.fft.fft2(gray))
                
                phase_spectrum = np.angle(fshift)
                # Map from [-pi, pi] to [0, 255]
                phase_mapped = ((phase_spectrum + np.pi) / (2 * np.pi) * 255)
                return Image.fromarray(np.clip(phase_mapped, 0, 255).astype(np.uint8))

            elif method == "inverseFFT":
                print("[ENGINE - FREQUENCY] Forcing Inverse FFT on image data...")
                # Note: Usually called on raw FFT data. If called on an image, we assume 
                # the image represents a shifted magnitude/complex array mapping.
                gray = np.array(target.convert("L"))
                # Treat the grayscale image as the shifted frequency domain data
                f_ishift = np.fft.ifftshift(gray)
                img_back = np.abs(np.fft.ifft2(f_ishift))
                
                # Normalize output to 0-255
                img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX)
                return Image.fromarray(img_back.astype(np.uint8))


            # ==========================================
            # EDGE DETECTION & FEATURE EXTRACTION
            # ==========================================
            elif method == "sobel":
                ksize = int(args[0]) if args else 3
                print(f"[ENGINE - VISION] Running Sobel Edge Detection (ksize={ksize})...")
                
                gray = np.array(target.convert("L"))
                grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
                grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
                
                magnitude = cv2.magnitude(grad_x, grad_y)
                magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                return Image.fromarray(magnitude)

            elif method == "scharr":
                print("[ENGINE - VISION] Running Scharr Edge Detection...")
                gray = np.array(target.convert("L"))
                grad_x = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
                grad_y = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
                
                magnitude = cv2.magnitude(grad_x, grad_y)
                magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                return Image.fromarray(magnitude)

            elif method == "laplacian":
                ksize = int(args[0]) if args else 3
                print(f"[ENGINE - VISION] Running Laplacian Edge Detection (ksize={ksize})...")
                
                gray = np.array(target.convert("L"))
                lap = cv2.Laplacian(gray, cv2.CV_64F, ksize=ksize)
                
                lap_abs = np.absolute(lap)
                lap_abs = cv2.normalize(lap_abs, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                return Image.fromarray(lap_abs)

            elif method == "canny":
                t1 = int(args[0]) if args else 100
                t2 = int(args[1]) if len(args) > 1 else 200
                print(f"[ENGINE - VISION] Running Canny Edge Detection (t1={t1}, t2={t2})...")
                
                gray = np.array(target.convert("L"))
                edges = cv2.Canny(gray, t1, t2)
                return Image.fromarray(edges)

            elif method == "harris":
                block_size = int(args[0]) if args else 2
                ksize = int(args[1]) if len(args) > 1 else 3
                k = float(args[2]) if len(args) > 2 else 0.04
                print(f"[ENGINE - VISION] Running Harris Corner Detection (blockSize={block_size}, k={k})...")
                
                gray = np.array(target.convert("L")).astype(np.float32)
                dst = cv2.cornerHarris(gray, block_size, ksize, k)
                
                # Dilate to mark the corners more clearly
                dst = cv2.dilate(dst, None)
                
                # Create a visual map where corners are white
                out = np.zeros_like(gray, dtype=np.uint8)
                out[dst > 0.01 * dst.max()] = 255
                return Image.fromarray(out)

            elif method == "shiTomasi":
                max_corners = int(args[0]) if args else 100
                q_level = float(args[1]) if len(args) > 1 else 0.01
                min_dist = float(args[2]) if len(args) > 2 else 10
                print(f"[ENGINE - VISION] Running Shi-Tomasi Corner Tracking (max={max_corners})...")
                
                gray = np.array(target.convert("L"))
                corners = cv2.goodFeaturesToTrack(gray, max_corners, q_level, min_dist)
                
                # Draw circles on the RGB image to show corners
                out_img = np.array(target.convert("RGB"))
                if corners is not None:
                    corners = np.int0(corners)
                    for i in corners:
                        x, y = i.ravel()
                        cv2.circle(out_img, (x, y), 3, (255, 0, 0), -1) # Red dots
                
                return Image.fromarray(out_img)

            elif method == "entropy":
                print("[ENGINE - METRICS] Calculating Shannon Entropy...")
                gray = np.array(target.convert("L"))
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
                hist = hist / hist.sum() # Normalize
                # Filter out zero probabilities to avoid log2(0)
                non_zero_hist = hist[hist > 0]
                entropy_val = -np.sum(non_zero_hist * np.log2(non_zero_hist))
                print(f" -> Entropy Score: {entropy_val:.4f}")
                return float(entropy_val)

            elif method == "sharpness":
                print("[ENGINE - METRICS] Calculating Sharpness (Variance of Laplacian)...")
                gray = np.array(target.convert("L"))
                sharpness_val = cv2.Laplacian(gray, cv2.CV_64F).var()
                print(f" -> Sharpness Score: {sharpness_val:.4f}")
                return float(sharpness_val)

            elif method == "noise":
                print("[ENGINE - METRICS] Estimating Image Noise...")
                gray = np.array(target.convert("L"))
                # Noise estimation using the standard deviation of a Laplacian filter
                lap = cv2.Laplacian(gray, cv2.CV_64F)
                noise_val = lap.std()
                print(f" -> Noise Estimate: {noise_val:.4f}")
                return float(noise_val)

            elif method in ["PSNR", "psnr"]:
                if not args:
                    raise ValueError("PSNR requires a second image for comparison.")
                print("[ENGINE - METRICS] Calculating Peak Signal-to-Noise Ratio (PSNR)...")
                img1 = np.array(target.convert("RGB")).astype(np.float64)
                img2 = np.array(args[0].convert("RGB").resize(target.size)).astype(np.float64)
                
                mse = np.mean((img1 - img2) ** 2)
                if mse == 0:
                    psnr_val = float('inf')
                else:
                    psnr_val = 20 * np.log10(255.0 / np.sqrt(mse))
                print(f" -> PSNR: {psnr_val:.2f} dB")
                return float(psnr_val)

            elif method in ["SSIM", "ssim"]:
                if not args:
                    raise ValueError("SSIM requires a second image for comparison.")
                print("[ENGINE - METRICS] Calculating Structural Similarity Index (SSIM)...")
                try:
                    from skimage.metrics import structural_similarity as compute_ssim
                except ImportError:
                    raise ImportError("SSIM requires the scikit-image library (pip install scikit-image).")
                
                img1 = np.array(target.convert("L"))
                img2 = np.array(args[0].convert("L").resize(target.size))
                ssim_val = compute_ssim(img1, img2)
                print(f" -> SSIM: {ssim_val:.4f}")
                return float(ssim_val)

            elif method == "objectCount":
                print("[ENGINE - ANALYSIS] Counting objects via Connected Components...")
                gray = np.array(target.convert("L"))
                # Otsu's automatic thresholding to separate objects from background
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, 4, cv2.CV_32S)
                count = num_labels - 1 # Subtract 1 for the background
                print(f" -> Objects Detected: {count}")
                
                # Draw bounding boxes on the image for visual feedback
                out_img = np.array(target.convert("RGB"))
                for i in range(1, num_labels):
                    x, y, w, h, area = stats[i]
                    cv2.rectangle(out_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Returns the annotated image (the AST variable will hold the visual result)
                return Image.fromarray(out_img)


            # ==========================================
            # GROUP 10: DATA VISUALIZATION & MAPPING
            # ==========================================
            
            elif method == "heatmap":
                cmap_name = args[0].upper() if args else "JET"
                print(f"[ENGINE - VISUALIZATION] Applying {cmap_name} Heatmap...")
                gray = np.array(target.convert("L"))
                
                # Map standard string names to OpenCV Colormap constants
                cmap_dict = {
                    "JET": cv2.COLORMAP_JET, "INFERNO": cv2.COLORMAP_INFERNO,
                    "VIRIDIS": cv2.COLORMAP_VIRIDIS, "HOT": cv2.COLORMAP_HOT,
                    "BONE": cv2.COLORMAP_BONE, "OCEAN": cv2.COLORMAP_OCEAN
                }
                cmap_code = cmap_dict.get(cmap_name, cv2.COLORMAP_JET)
                
                heatmap_img = cv2.applyColorMap(gray, cmap_code)
                return Image.fromarray(cv2.cvtColor(heatmap_img, cv2.COLOR_BGR2RGB))

            elif method == "falseColor":
                print("[ENGINE - VISUALIZATION] Generating False Color Composite...")
                arr = np.array(target.convert("RGB"))
                fc = np.zeros_like(arr)
                
                # Default false color shifts bands (R=G, G=B, B=R) - common in remote sensing
                fc[:, :, 0] = arr[:, :, 1]  # Red channel gets Green data
                fc[:, :, 1] = arr[:, :, 2]  # Green channel gets Blue data
                fc[:, :, 2] = arr[:, :, 0]  # Blue channel gets Red data
                return Image.fromarray(fc)

            elif method == "depthMap":
                if not args:
                    raise ValueError("depthMap requires a second image (stereo right/left pair) to calculate disparity.")
                print("[ENGINE - 3D] Calculating Stereo Disparity Depth Map...")
                
                imgL = np.array(target.convert("L"))
                imgR = np.array(args[0].convert("L").resize(target.size))
                
                # Block Matching algorithm for stereo disparity
                stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
                disparity = stereo.compute(imgL, imgR)
                
                # Normalize disparity to standard 0-255 image map
                disp_viz = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                return Image.fromarray(disp_viz)

            elif method == "vectorField":
                step = int(args[0]) if args else 16
                print(f"[ENGINE - VISUALIZATION] Rendering Gradient Vector Field (grid step={step})...")
                
                gray = np.array(target.convert("L"))
                out_img = np.array(target.convert("RGB"))
                
                # Calculate X and Y gradients
                grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
                grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
                
                # Draw arrows (quiver plot) over the original image
                for y in range(0, gray.shape[0], step):
                    for x in range(0, gray.shape[1], step):
                        gx = grad_x[y, x]
                        gy = grad_y[y, x]
                        end_x = int(x + gx * 0.05)
                        end_y = int(y + gy * 0.05)
                        cv2.arrowedLine(out_img, (x, y), (end_x, end_y), (0, 255, 0), 1, tipLength=0.3)
                        
                return Image.fromarray(out_img)

            # ==========================================
            # GROUP 11: DRAWING & VECTOR PRIMITIVES
            # ==========================================

            elif method == "line":
                x1 = int(args[0]) if len(args) > 0 else 0
                y1 = int(args[1]) if len(args) > 1 else 0
                x2 = int(args[2]) if len(args) > 2 else target.width
                y2 = int(args[3]) if len(args) > 3 else target.height
                color = args[4] if len(args) > 4 else "red"
                width = int(args[5]) if len(args) > 5 else 2
                print(f"[ENGINE - DRAWING] Drawing Line from ({x1},{y1}) to ({x2},{y2})...")

                res = target.copy()
                draw = ImageDraw.Draw(res)
                draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
                return res

            elif method == "circle":
                cx = int(args[0]) if len(args) > 0 else target.width // 2
                cy = int(args[1]) if len(args) > 1 else target.height // 2
                r = int(args[2]) if len(args) > 2 else 50
                color = args[3] if len(args) > 3 else "red"
                width = int(args[4]) if len(args) > 4 else 2
                print(f"[ENGINE - DRAWING] Drawing Circle at ({cx},{cy}) with radius {r}...")

                res = target.copy()
                draw = ImageDraw.Draw(res)
                bbox = [(cx - r, cy - r), (cx + r, cy + r)]
                draw.ellipse(bbox, outline=color, width=width)
                return res

            elif method == "rectangle":
                x1 = int(args[0]) if len(args) > 0 else 0
                y1 = int(args[1]) if len(args) > 1 else 0
                x2 = int(args[2]) if len(args) > 2 else target.width
                y2 = int(args[3]) if len(args) > 3 else target.height
                color = args[4] if len(args) > 4 else "red"
                width = int(args[5]) if len(args) > 5 else 2
                print(f"[ENGINE - DRAWING] Drawing Rectangle from ({x1},{y1}) to ({x2},{y2})...")

                res = target.copy()
                draw = ImageDraw.Draw(res)
                draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=width)
                return res

            elif method == "ellipse":
                x1 = int(args[0]) if len(args) > 0 else 0
                y1 = int(args[1]) if len(args) > 1 else 0
                x2 = int(args[2]) if len(args) > 2 else target.width
                y2 = int(args[3]) if len(args) > 3 else target.height
                color = args[4] if len(args) > 4 else "red"
                width = int(args[5]) if len(args) > 5 else 2
                print(f"[ENGINE - DRAWING] Drawing Ellipse in bounding box ({x1},{y1}) to ({x2},{y2})...")

                res = target.copy()
                draw = ImageDraw.Draw(res)
                draw.ellipse([(x1, y1), (x2, y2)], outline=color, width=width)
                return res

            elif method == "polygon":
                pts = args[0] if len(args) > 0 else []
                color = args[1] if len(args) > 1 else "red"
                width = int(args[2]) if len(args) > 2 else 2
                print(f"[ENGINE - DRAWING] Drawing Polygon with {len(pts)} points...")

                res = target.copy()
                draw = ImageDraw.Draw(res)
                if pts:
                    if isinstance(pts[0], (list, tuple)):
                        poly_points = [tuple(p) for p in pts]
                    else:
                        poly_points = [(pts[i], pts[i+1]) for i in range(0, len(pts), 2)]
                    
                    # Connect points in a closed loop with width support
                    poly_closed = poly_points + [poly_points[0]]
                    draw.line(poly_closed, fill=color, width=width)
                return res

            elif method == "text":
                txt = str(args[0]) if len(args) > 0 else ""
                x = int(args[1]) if len(args) > 1 else 10
                y = int(args[2]) if len(args) > 2 else 10
                font_size = int(args[3]) if len(args) > 3 else 20
                color = args[4] if len(args) > 4 else "white"
                print(f"[ENGINE - DRAWING] Rendering text '{txt}' at ({x},{y})...")

                res = target.copy()
                draw = ImageDraw.Draw(res)
                
                try:
                    from PIL import ImageFont
                    font = ImageFont.truetype("arial.ttf", font_size)
                except Exception:
                    from PIL import ImageFont
                    font = ImageFont.load_default()

                draw.text((x, y), txt, fill=color, font=font)
                return res

            elif method == "arrow":
                x1 = int(args[0]) if len(args) > 0 else 0
                y1 = int(args[1]) if len(args) > 1 else 0
                x2 = int(args[2]) if len(args) > 2 else target.width
                y2 = int(args[3]) if len(args) > 3 else target.height
                color_arg = args[4] if len(args) > 4 else "red"
                thickness = int(args[5]) if len(args) > 5 else 2
                print(f"[ENGINE - DRAWING] Drawing Arrow from ({x1},{y1}) to ({x2},{y2})...")

                if isinstance(color_arg, str):
                    from PIL import ImageColor
                    rgb = ImageColor.getrgb(color_arg)
                elif isinstance(color_arg, (list, tuple)):
                    rgb = tuple(color_arg[:3])
                else:
                    rgb = (255, 0, 0)

                bgr = (rgb[2], rgb[1], rgb[0])
                cv_img = cv2.cvtColor(np.array(target.convert("RGB")), cv2.COLOR_RGB2BGR)
                
                cv2.arrowedLine(cv_img, (x1, y1), (x2, y2), bgr, thickness, tipLength=0.2)
                return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

            


        raise AttributeError(f"Unknown method '{method}' on object {target}")
    
interpreter = Interpreter()

# while True:
#     code = input("Enter your code: ")

#     if not code.strip():
#         continue

#     try:
#         tokens = lexer(code)
#         parser = Parser(tokens)
#         ast = parser.parse()

#         # Run the interpreter!
#         output = interpreter.visit(ast)
        
#         # Display output if there is one
#         if output is not None:
#             print(output)

#     except Exception as e:
#         print("Runtime Error:", e)

code = """
func Aura():
    print("Aura")

Aura()
"""

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

# Run the interpreter!
output = interpreter.visit(ast)
        
# Display output if there is one
if output is not None:
    print(output) 


"""
HIT137 Group Assignment 2 - Question 2

"""


import os
import math


# ---------------------------------------------------------
# TOKENISER
# ---------------------------------------------------------

def tokenize(text):
    """
    Convert an expression into tokens.

    Valid tokens:
    NUM
    OP
    LPAREN
    RPAREN
    END
    """

    tokens = []
    i = 0

    while i < len(text):

        character = text[i]

        # Ignore spaces and tabs
        if character.isspace():
            i += 1
            continue

        # Number
        if character.isdigit():

            start = i

            # Read digits
            while i < len(text) and text[i].isdigit():
                i += 1

            # Optional decimal part
            if i < len(text) and text[i] == '.':
                i += 1

                # Decimal point must be followed by digits
                if i >= len(text) or not text[i].isdigit():
                    raise ValueError("Invalid number")

                while i < len(text) and text[i].isdigit():
                    i += 1

            number = text[start:i]

            tokens.append(("NUM", number))
            continue

        # Operators
        if character in "+-*/%^":
            tokens.append(("OP", character))
            i += 1
            continue

        # Opening parenthesis
        if character == '(':
            tokens.append(("LPAREN", character))
            i += 1
            continue

        # Closing parenthesis
        if character == ')':
            tokens.append(("RPAREN", character))
            i += 1
            continue

        # Anything else is invalid
        raise ValueError("Invalid character")

    tokens.append(("END", ""))

    return tokens


# ---------------------------------------------------------
# PARSER
# ---------------------------------------------------------

class Parser:
    """
    Recursive descent parser.

    Precedence from lowest to highest:

    1. + -
    2. * / % and implicit multiplication
    3. unary -
    4. ^

    The class is used internally only for keeping parser
    position/state. The assignment evaluator is built from
    functions and does not use an expression-tree class.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        """Return the current token."""
        return self.tokens[self.position]

    def consume(self):
        """Return the current token and move forward."""
        token = self.current()
        self.position += 1
        return token

    def match(self, token_type, value=None):
        """Check whether the current token matches."""
        token = self.current()

        if token[0] != token_type:
            return False

        if value is not None and token[1] != value:
            return False

        return True

    def parse(self):
        """
        Start parsing the complete expression.
        """

        node = self.expression()

        if not self.match("END"):
            raise ValueError("Unexpected token")

        return node

    # -----------------------------------------------------
    # Level 1: + and -
    # -----------------------------------------------------

    def expression(self):
        """
        expression -> term ((+ | -) term)*
        """

        node = self.term()

        while (
            self.match("OP", "+")
            or self.match("OP", "-")
        ):

            operator = self.consume()[1]

            right = self.term()

            node = (
                "bin",
                operator,
                node,
                right
            )

        return node

    # -----------------------------------------------------
    # Level 2: * / % and implicit multiplication
    # -----------------------------------------------------

    def term(self):
        """
        term -> unary ((* | / | %) unary)*
                with valid implicit multiplication.

        Valid implicit multiplication examples:

        2(3)
        2(3 + 4)
        (2)3
        (2)(3)
        """

        node = self.unary()

        while True:

            # Normal multiplication operators
            if (
                self.match("OP", "*")
                or self.match("OP", "/")
                or self.match("OP", "%")
            ):

                operator = self.consume()[1]

                right = self.unary()

                node = (
                    "bin",
                    operator,
                    node,
                    right
                )

                continue

            # Implicit multiplication before (
            if self.match("LPAREN"):

                right = self.unary()

                node = (
                    "bin",
                    "*",
                    node,
                    right
                )

                continue

            # Implicit multiplication after a parenthesised
            # expression followed by a number.
            if (
                self.match("NUM")
                and node[0] == "group"
            ):

                right = self.unary()

                node = (
                    "bin",
                    "*",
                    node,
                    right
                )

                continue

            break

        return node

    # -----------------------------------------------------
    # Level 3: unary -
    # -----------------------------------------------------

    def unary(self):
        """
        unary -> - unary
               | power

        Unary + is deliberately not supported.
        """

        # Unary + is invalid
        if self.match("OP", "+"):
            raise ValueError("Unary plus is not supported")

        # Unary -
        if self.match("OP", "-"):

            self.consume()

            operand = self.unary()

            return (
                "neg",
                operand
            )

        return self.power()

    # -----------------------------------------------------
    # Level 4: exponentiation
    # -----------------------------------------------------

    def power(self):
        """
        power -> primary (^ unary)?

        This makes exponentiation right-associative.

        Example:

        2 ^ 3 ^ 2

        becomes:

        (^ 2 (^ 3 2))
        """

        node = self.primary()

        if self.match("OP", "^"):

            self.consume()

            right = self.unary()

            node = (
                "bin",
                "^",
                node,
                right
            )

        return node

    # -----------------------------------------------------
    # Primary values
    # -----------------------------------------------------

    def primary(self):
        """
        primary -> number
                 | ( expression )
        """

        # Number
        if self.match("NUM"):

            value = self.consume()[1]

            return (
                "num",
                value
            )

        # Parenthesised expression
        if self.match("LPAREN"):

            self.consume()

            node = self.expression()

            if not self.match("RPAREN"):
                raise ValueError("Missing closing parenthesis")

            self.consume()

            # Keep information that the expression was
            # enclosed in parentheses. This is needed to
            # correctly recognise implicit multiplication.
            return (
                "group",
                node
            )

        raise ValueError("Expected number or '('")


# ---------------------------------------------------------
# TREE
# ---------------------------------------------------------

def tree_to_string(node):
    """
    Convert the internal parse tree into the required
    output format.
    """

    node_type = node[0]

    # Number
    if node_type == "num":
        return format_number_literal(node[1])

    # Parentheses are not shown in the tree unless they
    # create an operation.
    if node_type == "group":
        return tree_to_string(node[1])

    # Unary negation
    if node_type == "neg":

        return (
            "(neg "
            + tree_to_string(node[1])
            + ")"
        )

    # Binary operation
    operator = node[1]
    left = node[2]
    right = node[3]

    return (
        "("
        + operator
        + " "
        + tree_to_string(left)
        + " "
        + tree_to_string(right)
        + ")"
    )


def format_number_literal(text):
    """
    Format a number for the tree.

    Whole numbers are shown without .0.
    """

    value = float(text)

    if value.is_integer():
        return str(int(value))

    return text


# ---------------------------------------------------------
# EVALUATION
# ---------------------------------------------------------

def evaluate_tree(node):
    """
    Evaluate the parse tree.
    """

    node_type = node[0]

    # Number
    if node_type == "num":
        return float(node[1])

    # Parenthesised expression
    if node_type == "group":
        return evaluate_tree(node[1])

    # Unary negative
    if node_type == "neg":
        return -evaluate_tree(node[1])

    # Binary operation
    operator = node[1]

    left = evaluate_tree(node[2])
    right = evaluate_tree(node[3])

    if operator == "+":
        return left + right

    if operator == "-":
        return left - right

    if operator == "*":
        return left * right

    if operator == "/":

        if right == 0:
            raise ValueError("Division by zero")

        return left / right

    if operator == "%":

        if right == 0:
            raise ValueError("Modulo by zero")

        return left % right

    if operator == "^":

        try:
            result = left ** right

        except (OverflowError, ValueError):
            raise ValueError("Invalid exponentiation")

        if isinstance(result, complex):
            raise ValueError("Invalid exponentiation")

        if not math.isfinite(result):
            raise ValueError("Invalid exponentiation")

        return result

    raise ValueError("Unknown operator")


# ---------------------------------------------------------
# TOKEN OUTPUT
# ---------------------------------------------------------

def tokens_to_string(tokens):
    """
    Convert tokens to the required output format.
    """

    output = []

    for token_type, value in tokens:

        if token_type == "END":
            output.append("[END]")

        else:
            output.append(
                f"[{token_type}:{value}]"
            )

    return " ".join(output)


# ---------------------------------------------------------
# RESULT FORMATTING
# ---------------------------------------------------------

def format_result(value):
    """
    Format the result according to the assignment.

    Whole numbers:
        8

    Decimal numbers:
        rounded to 4 decimal places
    """

    if float(value).is_integer():
        return int(value)

    return round(value, 4)


# ---------------------------------------------------------
# SINGLE EXPRESSION
# ---------------------------------------------------------

def evaluate_expression(expression):
    """
    Tokenise, parse and evaluate one expression.

    Parsing errors return ERROR for tree, tokens and result.

    Evaluation errors such as division by zero keep the
    valid tree and tokens but return ERROR for the result.
    """

    try:

        # Tokenise
        tokens = tokenize(expression)

        # Parse
        parser = Parser(tokens)

        tree = parser.parse()

    except ValueError:

        return {
            "input": expression,
            "tree": "ERROR",
            "tokens": "ERROR",
            "result": "ERROR"
        }

    # Convert tree to required format
    tree_string = tree_to_string(tree)

    # Convert tokens to required format
    token_string = tokens_to_string(tokens)

    # Evaluate
    try:

        value = evaluate_tree(tree)

        result = format_result(value)

    except (ValueError, OverflowError, ZeroDivisionError):

        result = "ERROR"

    return {
        "input": expression,
        "tree": tree_string,
        "tokens": token_string,
        "result": result
    }


# ---------------------------------------------------------
# REQUIRED FUNCTION
# ---------------------------------------------------------

def evaluate_file(input_path: str) -> list[dict]:
    """
    Read expressions from input_path.

    Write output.txt in the same directory.

    Return a list of dictionaries containing:
        input
        tree
        tokens
        result
    """

    # Convert input path to absolute path
    input_path = os.path.abspath(input_path)

    # output.txt must be in the same directory
    output_path = os.path.join(
        os.path.dirname(input_path),
        "output.txt"
    )

    results = []
    

    # Read input
    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as input_file:

        expressions = input_file.read().splitlines()

    # Evaluate every expression
    for expression in expressions:

        result = evaluate_expression(expression)

        results.append(result)

    # Write output
    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as output_file:

        for index, result in enumerate(results):

            output_file.write(
                "Input: "
                + result["input"]
                + "\n"
            )

            output_file.write(
                "Tree: "
                + result["tree"]
                + "\n"
            )

            output_file.write(
                "Tokens: "
                + result["tokens"]
                + "\n"
            )

            output_file.write(
                "Result: "
                + str(result["result"])
                + "\n"
            )

            # Blank line between expressions
            if index < len(results) - 1:
                output_file.write("\n")

    return results


# ---------------------------------------------------------
# PROGRAM START
# ---------------------------------------------------------

if __name__ == "__main__":

    evaluate_file("input.txt")


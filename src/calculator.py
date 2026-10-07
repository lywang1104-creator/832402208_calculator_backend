"""
calculator.py - Hand-written RPN (postfix) expression evaluator
Core algorithm:
  1. _tokenize()      - Split expression string into tokens (numbers, ops, parens)
  2. _to_postfix()    - Convert infix to postfix (Shunting-yard algorithm)
  3. _eval_postfix()  - Evaluate postfix and return float
No eval / exec used anywhere — pure algorithm implementation.
"""

# Operator precedence table
OP_PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    'u-': 3,   # Unary minus (internal marker)
}

# Whether each operator is right-associative
OP_RIGHT_ASSOC = {
    '+': False,
    '-': False,
    '*': False,
    '/': False,
    'u-': True,
}

# Allowed character set
LEGAL_CHARS = set('0123456789+-*/(). ')


class ExpressionError(Exception):
    """Raised when the expression cannot be parsed or evaluated."""
    pass


class DivideByZeroError(ExpressionError):
    """Raised on division by zero."""
    pass


def _validate_chars(expression: str) -> None:
    """Ensure every character in the expression is legal."""
    for ch in expression:
        if ch not in LEGAL_CHARS:
            raise ExpressionError(f"Illegal character: '{ch}'")


def _tokenize(expression: str) -> list:
    """
    Split expression string into a token list.
    Returns: [number_str, operator, paren, ...]
    Handles: decimals, negative numbers (unary minus marked as 'u-')
    """
    expr = expression.strip()
    if not expr:
        raise ExpressionError("Expression is empty")

    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        # Skip whitespace
        if ch == ' ':
            i += 1
            continue

        # Number (including decimals)
        if ch.isdigit() or ch == '.':
            num_str = ''
            dot_count = 0
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.':
                    dot_count += 1
                    if dot_count > 1:
                        raise ExpressionError(
                            f"Malformed number (multiple dots) near position {i}"
                        )
                num_str += expr[i]
                i += 1
            if num_str == '.':
                raise ExpressionError("A dot alone is not a valid number")
            tokens.append(num_str)
            continue

        # Parentheses
        if ch in '()':
            tokens.append(ch)
            i += 1
            continue

        # Operators (+ - * /)
        if ch in '+-*/':
            # Detect unary minus / unary plus
            prev_is_op = (not tokens) or (tokens[-1] in '+-*/(')
            if ch == '-' and prev_is_op:
                tokens.append('u-')
            elif ch == '+' and prev_is_op:
                # Unary plus is just skipped
                pass
            else:
                tokens.append(ch)
            i += 1
            continue

        # Any other character should have been caught by _validate_chars
        raise ExpressionError(f"Unexpected character: '{ch}'")

    return tokens


def _check_brackets(tokens: list) -> None:
    """Verify parentheses are balanced."""
    stack = []
    for tok in tokens:
        if tok == '(':
            stack.append(tok)
        elif tok == ')':
            if not stack:
                raise ExpressionError("Unbalanced parentheses: extra closing ')'")
            stack.pop()
    if stack:
        raise ExpressionError("Unbalanced parentheses: extra opening '('")


def _to_postfix(tokens: list) -> list:
    """
    Shunting-yard algorithm: infix token list → postfix (RPN) list.
    """
    output = []       # Output queue
    op_stack = []     # Operator stack

    for token in tokens:
        # Number → enqueue directly
        if token not in OP_PRECEDENCE and token not in ('(', ')'):
            output.append(token)
            continue

        # Left paren → push
        if token == '(':
            op_stack.append(token)
            continue

        # Right paren → pop until matching '('
        if token == ')':
            while op_stack and op_stack[-1] != '(':
                output.append(op_stack.pop())
            if not op_stack:
                raise ExpressionError("Unbalanced parentheses")
            op_stack.pop()  # discard '('
            continue

        # Operator → handle precedence
        while op_stack:
            top = op_stack[-1]
            if top == '(':
                break
            top_prec = OP_PRECEDENCE[top]
            cur_prec = OP_PRECEDENCE[token]
            if top_prec > cur_prec or (top_prec == cur_prec and not OP_RIGHT_ASSOC[token]):
                output.append(op_stack.pop())
            else:
                break
        op_stack.append(token)

    # Pop any remaining operators from stack
    while op_stack:
        top = op_stack.pop()
        if top in ('(', ')'):
            raise ExpressionError("Unbalanced parentheses")
        output.append(top)

    return output


def _eval_postfix(postfix: list) -> float:
    """
    Evaluate a postfix (RPN) token list and return the float result.
    """
    stack = []

    for token in postfix:
        # Number → push onto stack
        if token not in OP_PRECEDENCE:
            try:
                stack.append(float(token))
            except ValueError:
                raise ExpressionError(f"Cannot parse number: '{token}'")
            continue

        # Unary minus
        if token == 'u-':
            if not stack:
                raise ExpressionError("Syntax error in expression")
            operand = stack.pop()
            stack.append(-operand)
            continue

        # Binary operators
        if len(stack) < 2:
            raise ExpressionError("Syntax error: operator missing operand")
        right = stack.pop()
        left = stack.pop()

        if token == '+':
            stack.append(left + right)
        elif token == '-':
            stack.append(left - right)
        elif token == '*':
            stack.append(left * right)
        elif token == '/':
            if right == 0:
                raise DivideByZeroError("Division by zero")
            stack.append(left / right)

    if len(stack) != 1:
        raise ExpressionError("Syntax error in expression")

    return stack[0]


def calculate(expression: str) -> float:
    """
    Public entry point for calculation.
    Full pipeline: char validation → tokenization → bracket check → to-postfix → eval.
    """
    _validate_chars(expression)
    tokens = _tokenize(expression)
    _check_brackets(tokens)
    postfix = _to_postfix(tokens)
    result = _eval_postfix(postfix)
    return result


def format_result(value: float) -> str:
    """Format result: integer shown as-is, otherwise up to 10 significant digits."""
    if value == int(value) and not (value != value):  # exclude NaN
        return str(int(value))
    # Strip trailing zeros via .10g
    formatted = f"{value:.10g}"
    return formatted
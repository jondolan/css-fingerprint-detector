import tinycss2
import re

def _is_complex_expression(value_str):
    # check for nested calc() expressions and immediately trigger a match
    if value_str.count('calc(') > 1:
        return True
        
    math_functions = [
        'sin(', 'cos(', 'tan(',
        'asin(', 'acos(', 'atan(',
        'exp(', 'log(',
        'sqrt(',
        # 'abs(', 'sign(',
        # 'min(', 'max('
    ]
    if any(fn in value_str for fn in math_functions):
        return True
        
    # check for operations with extreme values
    numbers = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', value_str)
    for num in numbers:
        try:
            value = float(num)
            # check for very large or very small numbers
            if abs(value) > 1000000 or (value != 0 and abs(value) < 0.0001):
                return True
        except ValueError:
            continue
        
    return False

def detector(css_text):
    results = []
    rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)

    for rule in rules:
        if rule.type == 'qualified-rule':
            block_content = tinycss2.parse_declaration_list(rule.content)
            for declaration in block_content:
                if declaration.type == 'declaration' and declaration.value:
                    value_as_string = tinycss2.serialize(declaration.value).lower()
                    if 'calc(' in value_as_string:
                        if _is_complex_expression(value_as_string):
                            results.append(value_as_string)
    return results

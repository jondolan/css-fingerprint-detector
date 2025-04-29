import tinycss2
import re

def detector(css_text):
    # detect css env() function usage that could be used for environment fingerprinting
    results = []
    rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
    
    env_patterns = [
        # safe area patterns (notch, rounded corners, etc.)
        (r'^safe-area-inset-', 'safe-area'),
        
        # keyboard patterns
        (r'^keyboard-inset-', 'keyboard'),
        
        # titlebar patterns
        (r'^titlebar-area-', 'titlebar'),
        
        # viewport segment patterns (foldable devices)
        (r'^viewport-segment-', 'foldable')
    ]
    
    for rule in rules:
        if rule.type == 'qualified-rule':
            declarations = tinycss2.parse_declaration_list(rule.content)
            for decl in declarations:
                if decl.type == 'declaration' and decl.value:
                    value = tinycss2.serialize(decl.value)
                    # look for env() function calls
                    env_matches = re.finditer(r'env\((.*?)\)', value)
                    for match in env_matches:
                        var_name = match.group(1).strip()
                        # check against known patterns
                        matched = False
                        for pattern, category in env_patterns:
                            if re.match(pattern, var_name):
                                results.append(f"env({var_name}) [{category}]")
                                matched = True
                                break
                        
                        if not matched:
                            # custom or unknown environment variable
                            results.append(f"env({var_name}) [custom]")
    
    return results

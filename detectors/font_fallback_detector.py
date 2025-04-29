import tinycss2
import re

def _parse_font_family_value(value_str):
    # parse a font-family value into a list of font names
    fonts = []
    # split on commas, but keep quoted strings intact
    in_quote = False
    quote_char = None
    current = []
    
    for char in value_str:
        if char in '"\'':
            if not in_quote:
                in_quote = True
                quote_char = char
            elif char == quote_char:
                in_quote = False
                quote_char = None
        elif char == ',' and not in_quote:
            font = ''.join(current).strip()
            if font:
                fonts.append(font)
            current = []
        else:
            current.append(char)
    
    # add the last font if any
    font = ''.join(current).strip()
    if font:
        fonts.append(font)
    
    return fonts

def _categorize_font(font):
    # categorize a font name into system, generic, or custom
    font = font.strip().strip('"\'').lower()
    
    # system fonts
    system_fonts = {
        'system-ui', '-apple-system', 'blinkmacsystemfont', 'segoe ui',
        'roboto', 'ubuntu', 'helvetica neue', 'arial', 'noto sans'
    }
    
    # generic families
    generic_families = {
        'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy',
        'system-ui', 'emoji', 'math', 'fangsong'
    }
    
    if font in system_fonts:
        return 'system'
    elif font in generic_families:
        return 'generic'
    else:
        return 'custom'

def _analyze_fallback_chain(fonts):
    # analyze a font fallback chain for fingerprinting potential
    if not fonts:
        return None
        
    categories = [_categorize_font(f) for f in fonts]
    
    # detect interesting patterns
    patterns = []
    
    # check if using system fonts with specific order
    system_fonts = [f for f, c in zip(fonts, categories) if c == 'system']
    if len(system_fonts) > 1:
        patterns.append(f"system-font-chain: {', '.join(system_fonts)}")
    
    # check if using custom fonts before system/generic
    if categories[0] == 'custom' and any(c in ['system', 'generic'] for c in categories[1:]):
        patterns.append(f"custom-with-fallback: {fonts[0]}")
    
    # check for unusual generic family placement (not at end)
    generic_positions = [i for i, c in enumerate(categories) if c == 'generic']
    if generic_positions and generic_positions[0] < len(categories) - 1:
        patterns.append("generic-family-not-last")
    
    # long fallback chains might be for fingerprinting
    if len(fonts) > 3:
        patterns.append(f"long-chain: {len(fonts)} fonts")
    
    return patterns

def detector(css_text):
    # detect potential font fallback chain based fingerprinting
    # looks for font-family declarations that might be used for system fingerprinting
    results = []
    rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
    
    def process_declarations(declarations, context=None):
        for decl in declarations:
            if decl.type == 'declaration' and decl.lower_name == 'font-family':
                value = tinycss2.serialize(decl.value)
                fonts = _parse_font_family_value(value)
                patterns = _analyze_fallback_chain(fonts)
                
                if patterns:
                    desc = f"font-family: {', '.join(fonts)}"
                    if context:
                        desc += f" [{context}]"
                    desc += f" ({'; '.join(patterns)})"
                    results.append(desc)
    
    for rule in rules:
        if rule.type == 'qualified-rule':
            if rule.content:
                declarations = tinycss2.parse_declaration_list(rule.content)
                process_declarations(declarations)
                
        elif rule.type == 'at-rule':
            # normalize prelude whitespace and remove extra spaces
            prelude = re.sub(r'\s+', ' ', tinycss2.serialize(rule.prelude).strip())
            context = f"@{rule.at_keyword} {prelude.strip()}"
            
            if rule.content:
                # handle nested rules in at-rules
                nested_rules = tinycss2.parse_rule_list(rule.content)
                for nested_rule in nested_rules:
                    if nested_rule.type == 'qualified-rule':
                        declarations = tinycss2.parse_declaration_list(nested_rule.content)
                        process_declarations(declarations, context)
    
    return results

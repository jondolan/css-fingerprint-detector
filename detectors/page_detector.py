import tinycss2

def detector(css_text):
    # detect @page rules that could be used for print detection and content manipulation
    results = []
    rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
    
    for rule in rules:
        if rule.type == 'at-rule' and rule.lower_at_keyword == 'page':
            # get the page rule content
            content = tinycss2.serialize(rule.content).strip() if rule.content else ''
            # get any prelude (e.g., @page :first)
            prelude = tinycss2.serialize(rule.prelude).strip() if rule.prelude else ''
            
            # check if the rule contains margin properties
            declarations = tinycss2.parse_declaration_list(rule.content)
            has_margins = any(
                decl.type == 'declaration' and 'margin' in decl.lower_name
                for decl in declarations
            )
            
            # include the type of page rule in the result
            rule_type = "margins" if has_margins else "basic"
            if prelude:
                results.append(f"@page {prelude} [{rule_type}]")
            else:
                results.append(f"@page [{rule_type}]")
    
    return results

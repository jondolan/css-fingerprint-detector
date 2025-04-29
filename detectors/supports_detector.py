import tinycss2

def detector(css_text):
    results = []
    rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)

    for rule in rules:
        if rule.type == 'at-rule' and rule.lower_at_keyword == 'supports':
            # Get the full supports rule including its condition
            condition = tinycss2.serialize(rule.prelude).strip() if rule.prelude else ''
            results.append(f"@supports {condition}")

    return results

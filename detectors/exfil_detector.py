import tinycss2
import re

def _clean_url(match):
    # clean a url match similar to the extension.js implementation
    url = match
    # remove quotes
    url = url.replace("'", "").replace('"', "")
    # remove resolution specifiers
    url = re.sub(r'\s+\d+x', '', url)
    # remove type declarations before removing wrappers
    url = re.sub(r'\s*type\([^)]*\)', '', url)
    # remove image-set, image, and url wrappers
    url = url.replace("image-set(", "").replace("image(", "").replace("url(", "")
    url = url.replace(")", "")
    return url

def _extract_urls_from_value(value_str):
    # extract and clean urls from a css value string
    urls = []
    
    # first find all image-set expressions (handling nested parentheses)
    image_set_pattern = r'image-set\(((?:[^()]+|\([^()]*\))*)\)'
    image_sets = re.finditer(image_set_pattern, value_str)
    for match in image_sets:
        content = match.group(1)
        # normalize whitespace and split on commas not inside parentheses
        content = re.sub(r'\s+', ' ', content).strip()
        parts = re.split(r',\s*(?![^()]*\))', content)
        for part in parts:
            url_match = re.search(r'["\']([^"\']+)["\']', part)
            if url_match:
                url = url_match.group(1)
                if url and not url.startswith('data:'):
                    urls.append({'url': url, 'type': 'image-set'})
    
    # then find all url() and image() expressions
    other_pattern = r'(url|image)\(([^)]+)\)'
    other_matches = re.finditer(other_pattern, value_str)
    for match in other_matches:
        func_type = match.group(1)
        content = match.group(2)
        url_match = re.search(r'["\']([^"\']+)["\']', content)
        if url_match:
            url = url_match.group(1)
            if url and not url.startswith('data:'):
                urls.append({'url': url, 'type': func_type})
    
    return urls

def _process_declaration(declaration, context=None):
    # process a css declaration for potential exfiltration urls
    results = []
    if declaration.type == 'declaration' and declaration.value:
        value = tinycss2.serialize(declaration.value)
        urls = _extract_urls_from_value(value)
        for url_info in urls:
            result = {
                'url': url_info['url'],
                'type': url_info['type'],
                'property': declaration.name,
                'context': context or 'declaration'
            }
            results.append(result)
    return results

def _process_at_rule(rule):
    # process an at-rule (like @media, @container) for potential exfiltration
    results = []
    # normalize prelude whitespace
    prelude = re.sub(r'\s+', ' ', tinycss2.serialize(rule.prelude).strip())
    context = f"{rule.at_keyword} {prelude}"
    
    if rule.content:
        # process nested rules within the at-rule
        nested_rules = tinycss2.parse_rule_list(rule.content)
        for nested_rule in nested_rules:
            if nested_rule.type == 'qualified-rule':
                declarations = tinycss2.parse_declaration_list(nested_rule.content)
                for decl in declarations:
                    results.extend(_process_declaration(decl, context))
            elif nested_rule.type == 'at-rule':
                results.extend(_process_at_rule(nested_rule))
    
    return results

def detector(css_text):
    # detect potential css-based data exfiltration using url patterns
    # looks for url(), image(), and image-set() usage that could be used for exfiltration
    results = []
    rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
    
    for rule in rules:
        if rule.type == 'qualified-rule':
            # process regular style rules
            declarations = tinycss2.parse_declaration_list(rule.content)
            for decl in declarations:
                results.extend(_process_declaration(decl))
                
        elif rule.type == 'at-rule':
            # process at-rules (media, container, supports, etc.)
            results.extend(_process_at_rule(rule))
    
    # format results for output
    formatted_results = []
    for r in results:
        desc = f"{r['type']}({r['url']}) in {r['property']}"
        if r['context'] != 'declaration':
            # add brackets to match expected format
            desc += f" [@{r['context']}]"
        formatted_results.append(desc)
    
    return formatted_results

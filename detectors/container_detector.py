import tinycss2
import re

def _find_container_styles(rules):
    # find all container style rules and their properties
    container_styles = {}
    container_props = {}
    
    for rule in rules:
        if rule.type == 'qualified-rule':
            selector = tinycss2.serialize(rule.prelude).strip()
            declarations = tinycss2.parse_declaration_list(rule.content)
            props = {}
            
            for decl in declarations:
                if decl.type == 'declaration':
                    value = tinycss2.serialize(decl.value).strip()
                    if decl.lower_name == 'container-type':
                        container_styles[selector] = value
                        props['container-type'] = value
                    elif decl.lower_name == 'width':
                        props['width'] = value
            
            if 'container-type' in props:
                container_props[selector] = props
                
    return container_styles, container_props

def _get_base_selector(selector):
    # get the base part of a selector (e.g., '#container' from '#container div')
    parts = selector.split(' ')
    return parts[0] if parts else selector

def _is_fingerprinting_pattern(container_rule, container_style, container_props):
    # analyze if a container query is being used for fingerprinting
    techniques = []
    
    # get the container query condition
    query = tinycss2.serialize(container_rule.prelude).strip() if container_rule.prelude else ''
    
    # get the container style (from container-type and other properties)
    container_type = container_props.get('container-type', '').strip('"\'').lower()
    width = container_props.get('width', '').lower()
    
    # check for font-relative units in container properties or query
    font_units = ['ch', 'ex', 'cap', 'ic']
    has_font_units = any(unit in width for unit in font_units) or any(unit in query for unit in font_units)
    if has_font_units:
        techniques.append("font-fingerprinting")
        
    # check for viewport-relative units in container properties or query
    viewport_units = ['vw', 'vh', 'vmin', 'vmax']
    has_viewport_units = any(unit in width for unit in viewport_units) or any(unit in query for unit in viewport_units)
    if has_viewport_units:
        techniques.append("viewport-fingerprinting")
        
    # check for element dimension measurements with precise values
    dimension_keywords = ['width', 'height', 'max-width', 'min-width', 'max-height', 'min-height']
    if any(x in query.lower() for x in dimension_keywords):
        # look for precise measurements that might target specific browsers/OS
        numbers = re.findall(r'[-+]?\d*\.?\d+', query)
        for num in numbers:
            if '.' in num or float(num) < 10:
                # Add dimension fingerprinting if we have font units (dual technique)
                # or if we're not using any other unit types
                if has_font_units or (not has_viewport_units and not has_font_units):
                    techniques.append("dimension-fingerprinting")
                break
    
    # check for text measurement via inline-size
    if container_type == 'inline-size' and not any(techniques):
        techniques.append("text-measurement")
                
    return techniques

def _find_matching_container(container_styles, container_props):
    # find the first container style and its properties
    # for container queries, we just need the first container we find
    # since the query applies to any container with the specified type
    if container_styles:
        selector = next(iter(container_styles))
        return container_styles[selector], container_props.get(selector, {})
    return None, {}

def detector(css_text):
    results = []
    rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
    
    # find all container styles first
    container_styles, container_props = _find_container_styles(rules)
    
    # get the container style and props (we only need one container for the query)
    style, props = _find_matching_container(container_styles, container_props)
    
    # analyze container queries
    for rule in rules:
        if rule.type == 'at-rule' and rule.lower_at_keyword == 'container':
            techniques = _is_fingerprinting_pattern(rule, style, props)
            query = tinycss2.serialize(rule.prelude).strip() if rule.prelude else ''
            for technique in techniques:
                results.append(f"@container {query} [{technique}]")

    return results

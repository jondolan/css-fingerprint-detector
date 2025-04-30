import tinycss2
import re

def _extract_container_name(query):
    """Extract container name from a container query."""
    # First try to find a name before the width condition
    if '(' in query:
        name = query[:query.index('(')].strip()
        if name:
            return name
            
    # If no explicit name found, look for container name in the query
    match = re.search(r'(\w+container)\s*[(/]', query)
    if match:
        return match.group(1)
    
    # Look for container name with format: container_name / inline-size
    match = re.search(r'(\w+)\s*/\s*inline-size', query)
    if match:
        return match.group(1)
    
    # Look for container name in CSS declarations
    match = re.search(r'container\s*:\s*(\w+)', query)
    if match:
        return match.group(1)
        
    return 'default'

def detector(css_text):
    results = []
    rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
    
    # Parse container declarations and queries directly from CSS text
    container_declarations = {}
    container_queries = {}
    
    # Find container declarations
    container_decl_pattern = re.compile(r'container\s*:\s*(\w+)\s*/\s*inline-size', re.IGNORECASE)
    for match in container_decl_pattern.finditer(css_text):
        container_name = match.group(1)
        container_declarations[container_name] = True
    
    # Find container queries
    container_query_pattern = re.compile(r'@container\s+(\w+)?\s*\(\s*(?:width|max-width|min-width)\s*(?::|\s*[><]=?|\s*=)\s*([-+]?\d*\.?\d+)(?:px|em|rem|ch|vw|vh|%)?\s*\)', re.IGNORECASE)
    for match in container_query_pattern.finditer(css_text):
        query_container_name = match.group(1) if match.group(1) else 'default'
        width_value = float(match.group(2))
        query = match.group(0)[10:].strip()  # Remove '@container ' prefix
        
        # Check if this query matches a declared container
        for declared_name in container_declarations:
            if declared_name in query or query_container_name == declared_name:
                query_container_name = declared_name
                break
        
        if query_container_name not in container_queries:
            container_queries[query_container_name] = {'dimensions': [], 'queries': []}
        
        container_queries[query_container_name]['dimensions'].append(width_value)
        container_queries[query_container_name]['queries'].append(query)
    
    # Second pass - check for matching dimensions that could indicate fingerprinting
    seen_queries = set()
    
    # First, process containers with multiple queries
    for container_name, container_info in container_queries.items():
        dimensions = container_info['dimensions']
        queries = container_info['queries']
        
        # If this container has multiple queries with different dimensions, mark all queries as suspicious
        if len(dimensions) > 1 and len(set(dimensions)) > 1:
            for q in queries:
                query_key = f"{q}|dimension-fingerprinting"
                if query_key not in seen_queries:
                    results.append(f"@container {q} [dimension-fingerprinting]")
                    seen_queries.add(query_key)
    
    # Then process individual queries for other suspicious patterns
    for rule in rules:
        if rule.type == 'at-rule' and rule.lower_at_keyword == 'container':
            query = tinycss2.serialize(rule.prelude).strip() if rule.prelude else ''
            container_name = _extract_container_name(query)
            
            # Skip queries that were already marked as suspicious due to multiple dimensions
            query_key = f"{query}|dimension-fingerprinting"
            if query_key in seen_queries:
                continue
                    
            width_pattern = re.search(r'(?:width|max-width|min-width)\s*(?::|\s*[><]=?|\s*=)\s*([-+]?\d*\.?\d+)(?:px|em|rem|ch|vw|vh|%)?', query.lower())
            
            if width_pattern:
                value = float(width_pattern.group(1))
                
                # Check for suspicious patterns:
                is_suspicious = False
                
                # Very specific decimal values
                if '.' in str(value):
                    is_suspicious = True
                    
                # Very small values
                if value < 10:
                    is_suspicious = True
                
                # Font-related terms in CSS
                font_terms = ['font-family', 'gill', 'arial', 'times', 'courier']
                if any(term in css_text.lower() for term in font_terms):
                    query_key = f"{query}|font-fingerprinting"
                    if query_key not in seen_queries:
                        results.append(f"@container {query} [font-fingerprinting]")
                        seen_queries.add(query_key)
                
                # Check individual query for suspicious patterns
                if is_suspicious:
                    query_key = f"{query}|dimension-fingerprinting"
                    if query_key not in seen_queries:
                        results.append(f"@container {query} [dimension-fingerprinting]")
                        seen_queries.add(query_key)
    
    return results

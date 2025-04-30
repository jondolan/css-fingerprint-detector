import tinycss2
import re

def detector(css_text):
    # detect image-set() function usage that could be used for resolution/dpi fingerprinting
    results = []
    rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
    
    for rule in rules:
        if rule.type == 'qualified-rule':
            declarations = tinycss2.parse_declaration_list(rule.content)
            for decl in declarations:
                if decl.type == 'declaration' and decl.value:
                    value = tinycss2.serialize(decl.value)
                    # look for image-set() function calls (including -webkit- prefix)
                    image_set_matches = re.finditer(r'(?:-webkit-)?image-set\(((?:[^()]+|\([^()]*\))*)\)', value)
                    for match in image_set_matches:
                        content = match.group(1).strip()
                        # extract resolution values
                        resolutions = []
                        # match resolution values after image URLs
                        res_matches = re.finditer(r'(?:"[^"]+"|\'[^\']+\')\s+(\d+(?:x|dpi|dpcm))', content)
                        for res_match in res_matches:
                            resolutions.append(res_match.group(1))
                        
                        # categorize based on resolution types, prioritizing device-pixel-ratio
                        category = "basic"  # default category
                        if resolutions:  # only change category if we found resolution values
                            if any('x' in res for res in resolutions):
                                category = "device-pixel-ratio"
                            elif any('dpi' in res for res in resolutions):
                                category = "dpi"
                            elif any('dpcm' in res for res in resolutions):
                                category = "dpcm"
                        
                        # include resolution values in result
                        res_str = ', '.join(resolutions) if resolutions else "no resolution"
                        results.append(f"image-set({res_str}) [{category}]")
    
    return results

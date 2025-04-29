from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from urllib.parse import urlparse, parse_qs
import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def _shorten_href(href):
    if not href:
        return None
    
    # Handle file:// URLs
    if href.startswith('file://'):
        return os.path.basename(href.replace('file:///', ''))
    
    # Handle http(s):// URLs
    parsed = urlparse(href)
    path_basename = os.path.basename(parsed.path)
    netloc = parsed.netloc

    if path_basename:  # normal file case
        return f"{netloc}/{path_basename}"

    # No basename, directory or dynamic resource
    query = parsed.query
    if query:
        params = parse_qs(query)
        if 'm' in params:
            mods = ",".join(params['m'])
            return f"(dynamic: {netloc}/{mods})"
        else:
            return f"(dynamic: {netloc})"
    
    return f"(dynamic: {netloc})"

def _get_domain(href):
    # extract domain from url
    if not href:
        return None
    if href.startswith('file://'):
        return 'local'
    parsed = urlparse(href)
    return parsed.netloc

def _calculate_chain_depths(G):
    # calculate depths of all paths in the graph
    depths = []
    source_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
    leaf_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]
    
    for source in source_nodes:
        for leaf in leaf_nodes:
            try:
                # find all paths from source to leaf
                paths = list(nx.all_simple_paths(G, source, leaf))
                for path in paths:
                    # path length is number of edges, which is nodes - 1
                    depths.append(len(path) - 1)
            except nx.NetworkXNoPath:
                continue
    
    if not depths:
        return 0, 0  # no paths found
    
    return sum(depths) / len(depths), max(depths)

def _lighten_color(color, amount=0.5):
    """Lightens the given color by multiplying (1-luminosity) by the given amount."""
    try:
        c = mcolors.to_rgb(color)
        return tuple([1 - amount * (1 - x) for x in c])
    except:
        return color

def analyze_css_loading(url, output_path, browser_type='chrome'):
    """
    Analyzes how CSS is loaded on a webpage and generates a directed graph visualization.
    
    Args:
        url (str): The URL of the webpage to analyze
        output_path (str): Path where to save the DAG visualization PNG
        browser_type (str): Type of browser to use ('chrome' or 'firefox')
        
    Returns:
        dict: Analysis results containing various metrics about CSS loading patterns
    """
    # setup headless browser
    if browser_type.lower() == 'chrome':
        options = ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
    else:  # firefox
        options = FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
    
    try:

        driver.get(url)

        # extract info about all stylesheets
        stylesheets = driver.execute_script("""
        let infos = [];
        for (let sheet of document.styleSheets) {
            try {
                let owner = sheet.ownerNode;
                let parent = owner.parentNode;
                
                // traverse up to find if ultimately in HEAD or BODY
                let root = parent;
                while (root && root.tagName !== 'HEAD' && root.tagName !== 'BODY' && root.tagName !== 'HTML') {
                    root = root.parentNode;
                }
                
                infos.push({
                    href: sheet.href,
                    ownerTag: owner.tagName,
                    ownerId: owner.id || null,
                    ownerClass: owner.className || null,
                    rootTag: root ? root.tagName : null,
                    parentTag: parent ? parent.tagName : null,
                    parentId: parent ? parent.id : null,
                    isDynamic: parent && parent.tagName !== 'HEAD'
                });
            } catch(e) {
                infos.push({href: null, error: e.toString()});
            }
        }
        return infos;
        """)

        # create directed graph
        G = nx.DiGraph()
        
        # track metrics
        dynamic_count = 0
        inline_count = 0
        external_count = 0
        domains = set()

        # define colors for hierarchy
        colors = {
            'head': '#2ca02c',    # green
            'body': '#d62728',    # red
            'head_child': _lighten_color('#2ca02c', 0.7),  # lighter green
            'body_child': _lighten_color('#d62728', 0.7)   # lighter red
        }

        # add HEAD and BODY as root nodes
        G.add_node("HEAD")
        G.add_node("BODY")

        # organize stylesheets by their root (HEAD or BODY)
        head_sheets = []
        body_sheets = []

        for sheet in stylesheets:
            # determine root (HEAD or BODY)
            root = sheet['rootTag']
            if not root or root == 'HTML':
                root = 'HEAD'  # default to HEAD if not found

            if root == 'HEAD':
                head_sheets.append(sheet)
            else:
                body_sheets.append(sheet)

        # process HEAD stylesheets
        for sheet in head_sheets:
            if sheet['href']:
                dest = _shorten_href(sheet['href'])
                external_count += 1
                domain = _get_domain(sheet['href'])
                if domain:
                    domains.add(domain)
            else:
                dest = f"Inline {inline_count} (in HEAD)"
                inline_count += 1
            G.add_edge("HEAD", dest)

        # process BODY stylesheets
        for sheet in body_sheets:
            if sheet.get('isDynamic'):
                # create intermediate node for dynamic element
                if sheet['parentId']:
                    parent_node = f"{sheet['parentTag']} #{sheet['parentId']}"
                    if not G.has_edge("BODY", parent_node):
                        G.add_edge("BODY", parent_node)
                    parent = parent_node
                else:
                    parent = "BODY"
                dynamic_count += 1
            else:
                parent = "BODY"

            if sheet['href']:
                dest = _shorten_href(sheet['href'])
                external_count += 1
                domain = _get_domain(sheet['href'])
                if domain:
                    domains.add(domain)
            else:
                dest = f"Inline {inline_count} (in {parent})"
                inline_count += 1

            G.add_edge(parent, dest)

        # calculate average and max chain depths
        avg_depth, max_depth = _calculate_chain_depths(G)

        # create the visualization
        plt.figure(figsize=(20, 20))
        
        # use shell layout with layers based on distance from roots
        layers = {}
        for node in G.nodes():
            # find shortest path from either HEAD or BODY
            try:
                head_dist = nx.shortest_path_length(G, "HEAD", node)
            except:
                head_dist = float('inf')
            try:
                body_dist = nx.shortest_path_length(G, "BODY", node)
            except:
                body_dist = float('inf')
            
            layer = min(head_dist, body_dist)
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(node)
        
        # create shell layout with layers
        pos = nx.shell_layout(G, nlist=list(layers.values()))
        
        # draw nodes by type with proper color formatting
        nx.draw_networkx_nodes(G, pos, nodelist=["HEAD"], node_color=[colors['head']] * 1, node_size=2500)
        nx.draw_networkx_nodes(G, pos, nodelist=["BODY"], node_color=[colors['body']] * 1, node_size=2500)
        
        # draw head children
        head_children = [n for n in G.neighbors("HEAD")]
        if head_children:
            nx.draw_networkx_nodes(G, pos, nodelist=head_children, 
                                 node_color=[colors['head_child']] * len(head_children), 
                                 node_size=2000)
        
        # draw body children
        body_children = []
        for n in G.neighbors("BODY"):
            body_children.append(n)
            # get grandchildren (stylesheets under dynamic elements)
            body_children.extend(list(G.neighbors(n)))
        if body_children:
            nx.draw_networkx_nodes(G, pos, nodelist=body_children, 
                                 node_color=[colors['body_child']] * len(body_children), 
                                 node_size=2000)
        
        # draw edges and labels
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True)
        nx.draw_networkx_labels(G, pos, font_size=10)
        
        # save the plot
        plt.savefig(output_path)
        plt.close()

        return {
            "browser": browser_type,
            "total_stylesheets": len(stylesheets),
            "dynamic_stylesheets": dynamic_count,
            "inline_styles": inline_count,
            "external_stylesheets": external_count,
            "unique_domains": len(domains),
            "avg_chain_depth": round(avg_depth, 2),
            "max_chain_depth": max_depth,
            "domains": list(domains)  # include list of domains for reference
        }

    finally:
        driver.quit()

# URL crawling
import requests
from bs4 import BeautifulSoup
from utils import same_domain, normalize_url
from datetime import datetime
from urllib.parse import urlparse
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import textwrap
import warnings

# Suppress BeautifulSoup markup warnings
warnings.filterwarnings('ignore', category=UserWarning, module='bs4')

def crawl_site(start_url, max_urls=50, timeout=5, depth_limit=3):
    """
    Crawl a website to discover URLs.
    
    Args:
        start_url: URL to start crawling from
        max_urls: Maximum number of URLs to discover (default: 50)
        timeout: Request timeout in seconds (default: 5)
        depth_limit: Maximum depth to crawl (default: 3)
    """
    visited = set()
    to_visit = [(start_url, 0)]  # (url, depth)
    # Always include start URL in scan target list.
    found_urls = {start_url}
    sitemap_data = []  # Store detailed URL info for sitemap
    url_graph = nx.DiGraph()  # Create directed graph for visualization
    url_graph.add_node(start_url, status="starting", depth=0)

    while to_visit and len(visited) < max_urls:
        url, depth = to_visit.pop(0)
        
        # Check depth limit
        if depth > depth_limit:
            continue
        
        if url in visited:
            continue

        try:
            res = requests.get(url, timeout=timeout)
            visited.add(url)
            
            # Store sitemap data
            url_info = {
                "url": url,
                "status_code": res.status_code,
                "content_type": res.headers.get("Content-Type", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "depth": depth
            }
            sitemap_data.append(url_info)
            
            # Update graph node with status
            url_graph.nodes[url]["status"] = res.status_code
            url_graph.nodes[url]["depth"] = depth

            # Validate response before parsing with BeautifulSoup
            if res.text and len(res.text.strip()) > 10:
                content_type = res.headers.get('content-type', '').lower()
                if 'html' in content_type or not content_type:
                    soup = BeautifulSoup(res.text, "html.parser")
                    for link in soup.find_all("a", href=True):
                        # Resolve relative links against the current page URL.
                        full_url = normalize_url(url, link["href"])
                        if same_domain(start_url, full_url):
                            found_urls.add(full_url)
                            if full_url not in url_graph:
                                url_graph.add_node(full_url, status="pending", depth=depth+1)
                            url_graph.add_edge(url, full_url)  # Add edge from current to linked URL
                            if full_url not in visited:
                                to_visit.append((full_url, depth + 1))

        except Exception as e:
            # Still add to sitemap with error info
            url_info = {
                "url": url,
                "status_code": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            sitemap_data.append(url_info)
            url_graph.nodes[url]["status"] = "error"
            continue

    # Generate sitemap image
    generate_sitemap_image(start_url, url_graph, sitemap_data)
    
    return list(found_urls)

def generate_sitemap_image(base_url, graph, sitemap_data):
    """Generate professional hierarchical sitemap with card-style nodes"""
    domain = urlparse(base_url).netloc.replace(".", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Ensure sitemap directory exists (relative to backend folder)
    sitemap_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sitemap")
    if not os.path.exists(sitemap_dir):
        os.makedirs(sitemap_dir)
    
    img_filename = os.path.join(sitemap_dir, f"sitemap_{domain}_{timestamp}.png")
    
    # Create figure with clean background
    total_nodes = max(len(graph.nodes()), 1)
    fig_width = min(max(20, total_nodes * 0.6), 60)
    fig_height = min(max(12, (len(graph.nodes()) // 6 + 1) * 4), 40)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor='#f5f5f5')
    ax.set_facecolor('#f5f5f5')
    
    # Calculate hierarchical positions manually for cleaner layout
    pos = {}
    levels = {}
    
    # BFS to assign levels
    start_node = list(graph.nodes())[0]
    visited = {start_node}
    queue = [(start_node, 0)]
    
    while queue:
        node, level = queue.pop(0)
        if level not in levels:
            levels[level] = []
        levels[level].append(node)
        
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, level + 1))
    
    # Position nodes by level
    max_level = max(levels.keys()) if levels else 0
    max_nodes_per_level = max((len(nodes) for nodes in levels.values()), default=1)
    for level, nodes in levels.items():
        y = 1.0 - (level / max(1, max_level) * 0.85) - 0.05  # Top to bottom with more spacing
        node_count = len(nodes)
        x_margin = 0.05
        for i, node in enumerate(nodes):
            x = x_margin + ((i + 1) / (node_count + 1)) * (1 - 2 * x_margin)  # Distribute evenly with margins
            pos[node] = (x, y)
    
    # Define color palette for different node types
    color_palette = {
        'home': '#6366F1',      # Indigo (starting point)
        'search': '#EC4899',    # Pink
        'content': '#14B8A6',   # Teal
        'info': '#8B5CF6',      # Purple
        'user': '#60A5FA',      # Light blue
        'action': '#F59E0B',    # Amber
        'error': '#EF4444',     # Red
        'pending': '#9CA3AF',   # Gray
    }
    
    # Assign colors based on URL patterns
    def get_node_color(node, status):
        if status == "starting":
            return color_palette['home']
        elif status == "error" or (isinstance(status, int) and status >= 400):
            return color_palette['error']
        elif status == "pending":
            return color_palette['pending']
        
        # Color by URL pattern
        path = urlparse(node).path.lower()
        if 'search' in path or 'results' in path:
            return color_palette['search']
        elif 'about' in path or 'contact' in path or 'info' in path:
            return color_palette['info']
        elif 'account' in path or 'profile' in path or 'user' in path:
            return color_palette['user']
        elif 'art' in path or 'gallery' in path or 'collection' in path:
            return color_palette['content']
        else:
            return color_palette['action']
    
    # Draw custom node boxes
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    
    node_data = {}
    for node in graph.nodes():
        if node not in pos:
            continue
            
        x, y = pos[node]
        status = graph.nodes[node].get("status", "unknown")
        color = get_node_color(node, status)
        
        # Get node info
        parsed = urlparse(node)
        path = parsed.path.strip('/') if parsed.path and parsed.path != '/' else 'Home'
        
        # Shorten path for display
        if len(path) > 30:
            parts = path.split('/')
            if len(parts) > 1:
                path = parts[-1]  # Last segment
            path = path[:27] + "..." if len(path) > 27 else path
        
        # Capitalize first letter
        display_name = path.replace('-', ' ').replace('_', ' ').title()
        display_name = "\n".join(textwrap.wrap(display_name, width=14)) or "Home"
        
        # Count outgoing links
        link_count = graph.out_degree(node)
        
        node_data[node] = {
            'pos': (x, y),
            'color': color,
            'name': display_name,
            'links': link_count
        }
        
        # Draw rounded rectangle card
        box_width = min(0.12, max(0.05, 0.9 / (max_nodes_per_level + 2)))
        box_height = 0.09 if max_level <= 2 else 0.075
        box = FancyBboxPatch(
            (x - box_width/2, y - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.005",
            facecolor=color,
            edgecolor='white',
            linewidth=3,
            transform=ax.transAxes,
            zorder=3
        )
        ax.add_patch(box)
        
        # Add icon symbol in the box
        icon_symbols = {
            'home': 'H', 'search': 'S', 'content': 'C',
            'info': 'I', 'user': 'U', 'action': 'A',
            'error': 'E', 'pending': 'P'
        }
        
        icon_type = 'home' if status == "starting" else (
            'error' if (status == "error" or (isinstance(status, int) and status >= 400)) else
            'pending' if status == "pending" else
            'search' if 'search' in path.lower() else
            'user' if 'account' in path.lower() or 'user' in path.lower() else
            'info' if 'about' in path.lower() or 'contact' in path.lower() else
            'content' if 'art' in path.lower() else 'action'
        )
        
        icon = icon_symbols.get(icon_type, 'A')
        ax.text(x, y + 0.015, icon, transform=ax.transAxes,
               fontsize=22, ha='center', va='center', zorder=4)
        
        # Add label below box
        ax.text(x, y - 0.06, display_name, transform=ax.transAxes,
               fontsize=9, ha='center', va='top', fontweight='bold',
               color='#1f2937', zorder=4)
        
        # Add link count below label
        ax.text(x, y - 0.085, f"{link_count} links", transform=ax.transAxes,
               fontsize=8, ha='center', va='top', color='#6b7280', zorder=4)
    
    # Draw edges with clean arrows
    for edge in graph.edges():
        if edge[0] not in pos or edge[1] not in pos:
            continue
            
        start_x, start_y = pos[edge[0]]
        end_x, end_y = pos[edge[1]]
        
        # Determine if it's a dashed line (for pending or error connections)
        target_status = graph.nodes[edge[1]].get("status", "unknown")
        linestyle = '--' if (target_status == "pending" or target_status == "error") else '-'
        
        arrow = FancyArrowPatch(
            (start_x, start_y - 0.04), (end_x, end_y + 0.04),
            transform=ax.transAxes,
            arrowstyle='->,head_width=0.35,head_length=0.5',
            color='#9ca3af',
            linewidth=2,
            linestyle=linestyle,
            alpha=0.6,
            zorder=1,
            connectionstyle="arc3,rad=0.1"
        )
        ax.add_patch(arrow)
    
    # Add title
    ax.text(0.5, 0.98, f"Site Structure Map", transform=ax.transAxes,
           fontsize=22, ha='center', va='top', fontweight='bold', color='#111827')
    ax.text(0.5, 0.955, base_url, transform=ax.transAxes,
           fontsize=12, ha='center', va='top', color='#6b7280')
    
    # Add legend in bottom right
    legend_x = 0.02
    legend_y = 0.15
    
    legend_box = FancyBboxPatch(
        (legend_x, legend_y - 0.13), 0.15, 0.13,
        boxstyle="round,pad=0.01",
        facecolor='white',
        edgecolor='#e5e7eb',
        linewidth=2,
        transform=ax.transAxes,
        zorder=2
    )
    ax.add_patch(legend_box)
    
    ax.text(legend_x + 0.075, legend_y - 0.01, "Legend", transform=ax.transAxes,
           fontsize=11, ha='center', va='top', fontweight='bold', color='#111827')
    
    legend_items = [
        ('solid', 'Active Connection'),
        ('dashed', 'Pending/Error'),
    ]
    
    y_offset = legend_y - 0.04
    for line_style, label in legend_items:
        ax.plot([legend_x + 0.01, legend_x + 0.03], [y_offset, y_offset],
               linestyle='-' if line_style == 'solid' else '--',
               color='#9ca3af', linewidth=2.5, transform=ax.transAxes)
        ax.text(legend_x + 0.04, y_offset, label, transform=ax.transAxes,
               fontsize=8, va='center', color='#4b5563')
        y_offset -= 0.025
    
    # Add stats in bottom left
    status_counts = {'success': 0, 'error': 0, 'pending': 0}
    for node in graph.nodes():
        status = graph.nodes[node].get("status", "unknown")
        if status == 200:
            status_counts['success'] += 1
        elif status == "error" or (isinstance(status, int) and status >= 400):
            status_counts['error'] += 1
        elif status == "pending":
            status_counts['pending'] += 1
    
    stats_x = 0.82
    stats_y = 0.15
    
    stats_box = FancyBboxPatch(
        (stats_x, stats_y - 0.13), 0.16, 0.13,
        boxstyle="round,pad=0.01",
        facecolor='white',
        edgecolor='#e5e7eb',
        linewidth=2,
        transform=ax.transAxes,
        zorder=2
    )
    ax.add_patch(stats_box)
    
    ax.text(stats_x + 0.08, stats_y - 0.01, "Statistics", transform=ax.transAxes,
           fontsize=11, ha='center', va='top', fontweight='bold', color='#111827')
    
    stats_text = f"""Total URLs: {len(graph.nodes())}
Connections: {len(graph.edges())}
Success: {status_counts['success']}
Errors: {status_counts['error']}
Pending: {status_counts['pending']}"""
    
    ax.text(stats_x + 0.02, stats_y - 0.04, stats_text, transform=ax.transAxes,
           fontsize=9, va='top', color='#4b5563', family='monospace')
    
    # Add timestamp
    timestamp_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ax.text(0.5, 0.01, timestamp_text, transform=ax.transAxes,
           fontsize=8, ha='center', va='bottom', color='#9ca3af')
    
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.axis('off')
    
    # Save with high quality
    plt.tight_layout(pad=1.0)
    plt.savefig(img_filename, dpi=300, bbox_inches='tight', 
                facecolor='#f5f5f5', edgecolor='none')
    plt.close()
    
    print(f"[✓] Professional sitemap saved: {img_filename}")
    print(f"    • {len(graph.nodes())} URLs mapped")
    print(f"    • {len(graph.edges())} connections discovered")
    print(f"    • {status_counts['success']} successful pages")
    
    return img_filename

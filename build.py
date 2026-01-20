import os
import re
import shutil
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Custom slugify function to support Unicode
def custom_slugify(value, separator='-'):
    slug = value.lower()
    slug = re.sub(r'<[^>]+>', '', slug) # Remove HTML tags
    slug = re.sub(r'[^\w\s-]', '', slug) # Remove special chars
    slug = slug.strip().replace(' ', separator)
    return slug

# Configuration
CONTENT_DIR = "."
OUTPUT_DIR = "dist"
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"

# Helper to parse metadata from Jinja2 set statements in Markdown
def parse_metadata(content):
    metadata = {}
    # Match {% set key = "value" %} or {% set key = 'value' %}
    pattern = r'\{%\s*set\s+(\w+)\s*=\s*["\'](.*?)["\']\s*%\}'
    matches = re.findall(pattern, content)
    for key, value in matches:
        metadata[key] = value
    return metadata

# Helper to extract H2 headers for TOC
def extract_h2(content):
    h2s = {}
    # Simple regex for Markdown headers: ## Header Text
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('## '):
            text = line.strip()[3:].strip()
            slug = custom_slugify(text)
            h2s[slug] = text
            
    return h2s

# Helper to extract title from content
def extract_title(content, default_title):
    metadata = parse_metadata(content)
    if 'section_title' in metadata:
        return metadata['section_title']
    
    # Try to find H1 header (Markdown)
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('# '):
            return line.strip()[2:].strip()
            
    # Try to find H2 header (Markdown) - sometimes used as top level
    for line in lines:
        if line.strip().startswith('## '):
            return line.strip()[3:].strip()
            
    # Try to find H1/H2 header (HTML)
    # Some files use <h2>Title</h2> as the main title
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    if h1_match:
        return h1_match.group(1).strip()
        
    h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.IGNORECASE | re.DOTALL)
    if h2_match:
        return h2_match.group(1).strip()
        
    return default_title

def build():

    print("Starting build...")
    
    # 1. Clean and create output directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # 2. Copy static files
    print(f"Copying static files from {STATIC_DIR} to {OUTPUT_DIR}/static")
    shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, "static"))

    # 3. Scan content directory to build the tree
    tree = {
        "chapters": [],
        "appendices": [],
        "sections": {}
    }

    # Regex to identify chapter directories: 01-account, A-privacy, etc.
    chapter_pattern = re.compile(r'^(\d+|[A-Z])-([a-z0-9-]+)$')

    items = []
    for entry in os.listdir(CONTENT_DIR):
        if os.path.isdir(entry):
            match = chapter_pattern.match(entry)
            if match:
                items.append((entry, match.group(1), match.group(2)))

    # Sort items: 01, 02... then A, B...
    items.sort()

    for entry, number, name in items:
        # Determine if it's a chapter or appendix
        is_chapter = number.isdigit()
        
        # Determine route base name (e.g., "account")
        route_base = name 
        
        # Read index.md to get title
        index_path = os.path.join(CONTENT_DIR, entry, "00-index.md")
        if not os.path.exists(index_path):
            continue
            
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        metadata = parse_metadata(content)
        title = extract_title(content, name.replace('-', ' ').title())
        subtitle = metadata.get('section_subtitle', '')
        
        section_info = {
            "chapter_number": number,
            "title": title,
            "subtitle": subtitle,
            "route": route_base,
            "dir": entry,
            "h2s": extract_h2(content),
            "is_appendix": not number.isdigit(),
            "nav": [route_base], # Used in chapters-list.html.j2
            "link": f"/{route_base}",
            "label": "下一章"
        }
        
        if is_chapter:
            tree["chapters"].append(name)
        else:
            tree["appendices"].append(name)
            
        if name not in tree["sections"]:
            tree["sections"][name] = []
        
        # Add index page as first item in section list
        tree["sections"][name].append(section_info)
        
        # Check for other files in the directory to add as subsections
        files = sorted(os.listdir(os.path.join(CONTENT_DIR, entry)))
        for fname in files:
            file_path = os.path.join(CONTENT_DIR, entry, fname)
            
            # Handle subdirectory (e.g., D-docs/01-cli)
            if os.path.isdir(file_path):
                # 1. Handle index page of the subdirectory
                sub_index_path = os.path.join(file_path, "00-index.md")
                if not os.path.exists(sub_index_path):
                    sub_index_path = os.path.join(file_path, "index.md")

                if os.path.exists(sub_index_path):
                    sub_name = fname
                    sub_name_clean = re.sub(r'^\d+-', '', sub_name)
                    sub_route = f"{route_base}/{sub_name_clean}"
                    
                    with open(sub_index_path, 'r', encoding='utf-8') as f:
                        sub_content = f.read()
                    
                    sub_metadata = parse_metadata(sub_content)
                    sub_title = extract_title(sub_content, sub_name_clean.replace('-', ' ').title())
                    
                    # For docs, we need structured nav: ['docs', 'cli', 'index']
                    sub_nav = [route_base, sub_name_clean, 'index']

                    sub_section_info = {
                        "chapter_number": number,
                        "title": sub_title,
                        "subtitle": sub_metadata.get('section_subtitle', ''),
                        "route": sub_route,
                        "dir": os.path.join(entry, fname),
                        "file": os.path.basename(sub_index_path),
                        "h2s": extract_h2(sub_content),
                        "is_appendix": not number.isdigit(),
                        "nav": sub_nav,
                        "link": f"/{sub_route}",
                        "label": "下一章"
                    }
                    tree["sections"][name].append(sub_section_info)
                
                # 2. Handle other markdown files in the subdirectory
                sub_files = sorted(os.listdir(file_path))
                for sub_fname in sub_files:
                    if sub_fname in ["00-index.md", "index.md"] or not sub_fname.endswith(".md"):
                        continue
                        
                    nested_name = sub_fname.replace('.md', '')
                    nested_name_clean = re.sub(r'^\d+-', '', nested_name)
                    # Route: docs/server/stellar
                    sub_dir_clean = re.sub(r'^\d+-', '', fname)
                    nested_route = f"{route_base}/{sub_dir_clean}/{nested_name_clean}"
                    
                    with open(os.path.join(file_path, sub_fname), 'r', encoding='utf-8') as f:
                        nested_content = f.read()
                        
                    nested_metadata = parse_metadata(nested_content)
                    nested_title = extract_title(nested_content, nested_name_clean.replace('-', ' ').title())
                    
                    # For docs sub-pages: ['docs', 'server', 'stellar']
                    nested_nav = [route_base, sub_dir_clean, nested_name_clean]

                    nested_section_info = {
                        "chapter_number": number,
                        "title": nested_title,
                        "subtitle": nested_metadata.get('section_subtitle', ''),
                        "route": nested_route,
                        "dir": os.path.join(entry, fname),
                        "file": sub_fname,
                        "h2s": extract_h2(nested_content),
                        "is_appendix": not number.isdigit(),
                        "nav": nested_nav,
                        "link": f"/{nested_route}",
                        "label": "下一章"
                    }
                    tree["sections"][name].append(nested_section_info)
                
                continue

            if fname == "00-index.md" or not fname.endswith(".md"):
                continue

            sub_name = fname.replace('.md', '')
            sub_name_clean = re.sub(r'^\d+-', '', sub_name)
            sub_route = f"{route_base}/{sub_name_clean}"
            
            with open(os.path.join(CONTENT_DIR, entry, fname), 'r', encoding='utf-8') as f:
                sub_content = f.read()
            
            sub_metadata = parse_metadata(sub_content)
            sub_title = extract_title(sub_content, sub_name_clean.replace('-', ' ').title())
            
            sub_section_info = {
                "chapter_number": number,
                "title": sub_title,
                "subtitle": sub_metadata.get('section_subtitle', ''),
                "route": sub_route,
                "dir": entry,
                "file": fname,
                "h2s": extract_h2(sub_content),
                "is_appendix": not number.isdigit(),
                "nav": [route_base, sub_name_clean],
                "link": f"/{sub_route}",
                "label": "下一章"
            }
            tree["sections"][name].append(sub_section_info)



    # 4. Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )

    # Custom filters and functions
    def url_for(endpoint, filename=None):
        if endpoint == 'static':
            return f"/static/{filename}"
        return f"/{endpoint}"

    def compose_content(docs_path, capture=None, html_in_markdown=True):
        # Resolve docs_path
        if docs_path == "home":
            full_path = os.path.join(CONTENT_DIR, "home.md")
        else:
            full_path = os.path.join(CONTENT_DIR, docs_path)
            
        if not os.path.exists(full_path):
            return f"File not found: {full_path}"
            
        with open(full_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
            
        # Extract metadata
        local_metadata = parse_metadata(raw_content)
        env.globals['_captured_vars'] = local_metadata
        
        # Remove Jinja2 set statements
        clean_content = re.sub(r'\{%\s*set\s+.*?%\}', '', raw_content)
        
        # Render Markdown
        html = markdown.markdown(
            clean_content, 
            extensions=['extra', 'toc', 'codehilite'],
            extension_configs={
                'toc': {
                    'slugify': custom_slugify
                }
            }
        )
        
        return html

    def compose_captured(var_name):
        return env.globals.get('_captured_vars', {}).get(var_name, '')

    env.globals['url_for'] = url_for
    env.globals['compose_content'] = compose_content
    env.globals['compose_captured'] = compose_captured
    env.globals['prefix'] = ""
    env.globals['STATIC_ASSET_MAP'] = {}
    
    # 5. Render pages
    print("Rendering pages...")
    
    # Home page
    try:
        template = env.get_template('home.html.j2')
        output = template.render(tree=tree)
        with open(os.path.join(OUTPUT_DIR, "index.html"), 'w', encoding='utf-8') as f:
            f.write(output)
        print("Generated index.html")
    except Exception as e:
        print(f"Error generating index.html: {e}")
        
    # Render all sections
    for section_name, section_list in tree["sections"].items():
        for i, section_info in enumerate(section_list):
            route = section_info["route"]
            
            if "file" in section_info:
                file_path = os.path.join(section_info["dir"], section_info["file"])
            else:
                file_path = os.path.join(section_info["dir"], "00-index.md")
                
            out_path = os.path.join(OUTPUT_DIR, route)
            if not os.path.exists(out_path):
                os.makedirs(out_path)
                
            # Determine nav_next
            nav_next = None
            if i + 1 < len(section_list):
                nav_next = section_list[i + 1]
            else:
                # Find next chapter
                # This is tricky because `tree["chapters"]` is a list of names.
                # We need to find the current chapter index and get the next one.
                pass 
                # Leaving simple for now, can improve later
            
            is_appendix = not section_info["chapter_number"].isdigit()
            
            try:
                template = env.get_template('chapter.html.j2')
                output = template.render(
                    tree=tree,
                    section=section_info,
                    sections=section_list,
                    docs_path=file_path,
                    nav_next=nav_next,
                    is_appendix=is_appendix
                )
                
                with open(os.path.join(out_path, "index.html"), 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Generated {out_path}/index.html")
            except Exception as e:
                print(f"Error generating {out_path}: {e}")

    print("Build complete.")

if __name__ == "__main__":
    build()

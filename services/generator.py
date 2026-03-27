import os
import shutil
import zipfile
from jinja2 import Environment, FileSystemLoader

def generate_portfolio(username: str, data: dict, theme: str = "light") -> str:
    """
    Generates static HTML and CSS files using Jinja2 templates,
    zips them, and returns the path to the zip file.
    """
    # Define paths based on the structure
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")
    
    # Output directory for this specific user's generated portfolio
    output_dir = os.path.join(base_dir, "generated_sites", username)
    os.makedirs(output_dir, exist_ok=True)
    
    # Jinja2 setup
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("portfolio.html")
    
    # Render HTML applying the extracted data AND theme
    html_content = template.render(data=data, theme=theme)
    
    # Save index.html
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Copy static assets (e.g. styles.css)
    output_static_dir = os.path.join(output_dir, "static")
    os.makedirs(output_static_dir, exist_ok=True)
    
    src_css = os.path.join(static_dir, "styles.css")
    if os.path.exists(src_css):
        shutil.copy(src_css, os.path.join(output_static_dir, "styles.css"))
        
    # Zip the generated files
    generated_sites_dir = os.path.join(base_dir, "generated_sites")
    zip_path = os.path.join(generated_sites_dir, f"{username}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Keep the folder structure inside the zip
                arcname = os.path.relpath(file_path, generated_sites_dir)
                zipf.write(file_path, arcname)
                
    return zip_path

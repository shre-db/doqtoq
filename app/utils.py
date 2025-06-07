def load_svg_icon(icon_path):
    """Load and return SVG icon as base64 encoded string"""
    try:
        with open(icon_path, 'r') as f:
            svg_content = f.read()
        import base64
        return base64.b64encode(svg_content.encode()).decode()
    except Exception as e:
        print(f"Error loading icon {icon_path}: {e}")
        return None
# Watermark Configuration
# This file contains all configurable settings for the watermark component

WATERMARK_CONFIG = {
    # Text content
    'text': 'Created by Monish Reddy',
    
    # Styling
    'font_size': '11px',
    'font_weight': '500',
    'color': 'rgba(0, 0, 0, 0.4)',
    'hover_color': '#3B82F6',  # Primary blue
    'click_color': '#10B981',  # Green for click feedback
    
    # Positioning
    'position': 'fixed',
    'bottom': '12px',
    'right': '12px',
    'z_index': '1000',
    
    # Spacing
    'padding': '4px 8px',
    'border_radius': '4px',
    
    # Mobile responsive
    'mobile_bottom': '8px',
    'mobile_right': '8px',
    'mobile_font_size': '10px',
    'mobile_padding': '3px 6px',
    
    # Animation
    'fade_in_duration': '0.5s',
    'hover_scale': '1.05',
    'click_scale': '0.98',
    'transition_duration': '0.3s',
    
    # Effects
    'text_shadow': '0 1px 2px rgba(255, 255, 255, 0.8)',
    'hover_text_shadow': '0 2px 4px rgba(59, 130, 246, 0.3)',
    'backdrop_filter': 'blur(2px)',
    
    # Dark mode support
    'dark_mode_color': 'rgba(255, 255, 255, 0.6)',
    'dark_mode_hover_color': '#60A5FA',
    'dark_mode_text_shadow': '0 1px 2px rgba(0, 0, 0, 0.8)',
    'dark_mode_hover_text_shadow': '0 2px 4px rgba(96, 165, 250, 0.4)',
    
    # Behavior
    'clickable': True,
    'redirect_url': None,  # Set to '/about' or '/contact' if you want to redirect
    'show_tooltip': True,
    'tooltip_text': 'Created by Monish Reddy',
    
    # Accessibility
    'keyboard_navigable': True,
    'screen_reader_friendly': True,
}

# Function to get watermark CSS dynamically
def get_watermark_css():
    """Generate CSS for watermark based on configuration"""
    config = WATERMARK_CONFIG
    
    css = f"""
    .watermark {{
        position: {config['position']};
        bottom: {config['bottom']};
        right: {config['right']};
        z-index: {config['z_index']};
        font-size: {config['font_size']};
        font-weight: {config['font_weight']};
        font-family: inherit;
        color: {config['color']};
        background: transparent;
        text-shadow: {config['text_shadow']};
        cursor: {'pointer' if config['clickable'] else 'default'};
        user-select: none;
        transition: all {config['transition_duration']} ease;
        animation: watermarkFadeIn {config['fade_in_duration']} ease-in;
        padding: {config['padding']};
        border-radius: {config['border_radius']};
        backdrop-filter: {config['backdrop_filter']};
    }}
    
    .watermark:hover {{
        transform: scale({config['hover_scale']});
        color: {config['hover_color']};
        text-shadow: {config['hover_text_shadow']};
    }}
    
    .watermark:active {{
        transform: scale({config['click_scale']});
    }}
    
    @keyframes watermarkFadeIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @media (max-width: 768px) {{
        .watermark {{
            bottom: {config['mobile_bottom']};
            right: {config['mobile_right']};
            font-size: {config['mobile_font_size']};
            padding: {config['mobile_padding']};
        }}
    }}
    
    @media (prefers-color-scheme: dark) {{
        .watermark {{
            color: {config['dark_mode_color']};
            text-shadow: {config['dark_mode_text_shadow']};
        }}
        
        .watermark:hover {{
            color: {config['dark_mode_hover_color']};
            text-shadow: {config['dark_mode_hover_text_shadow']};
        }}
    }}
    """
    
    return css

# Function to get watermark HTML
def get_watermark_html():
    """Generate HTML for watermark based on configuration"""
    config = WATERMARK_CONFIG
    
    onclick = f"handleWatermarkClick()" if config['clickable'] else ""
    title = f'title="{config["tooltip_text"]}"' if config['show_tooltip'] else ""
    
    html = f'<div class="watermark" {onclick and f"onclick=\"{onclick}\""} {title}>{config["text"]}</div>'
    
    return html

# Function to get watermark JavaScript
def get_watermark_js():
    """Generate JavaScript for watermark based on configuration"""
    config = WATERMARK_CONFIG
    
    if not config['clickable']:
        return ""
    
    js = f"""
    function handleWatermarkClick() {{
        const watermark = document.querySelector('.watermark');
        
        // Add click effect
        watermark.style.transform = 'scale({config["click_scale"]})';
        watermark.style.color = '{config["click_color"]}';
        
        // Reset after animation
        setTimeout(() => {{
            watermark.style.transform = '';
            watermark.style.color = '';
        }}, 200);
        
        // Redirect if URL is configured
        {f"window.location.href = '{config['redirect_url']}';" if config['redirect_url'] else ""}
    }}
    
    // Keyboard accessibility
    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Enter' && document.activeElement.classList.contains('watermark')) {{
            handleWatermarkClick();
        }}
    }});
    """
    
    return js

if __name__ == "__main__":
    # Example usage
    print("Watermark CSS:")
    print(get_watermark_css())
    print("\nWatermark HTML:")
    print(get_watermark_html())
    print("\nWatermark JavaScript:")
    print(get_watermark_js())

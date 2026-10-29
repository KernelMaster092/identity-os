import os

def apply_mobile_fix():
    file_path = os.path.join('public', 'index.html')
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Viewport for better mobile scaling
    viewport_old = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
    viewport_new = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">'
    content = content.replace(viewport_old, viewport_new)

    # 2. Inject the Mobile CSS
    # We target the closing </style> tag to append our responsive rules
    mobile_css = """
        /* MOBILE RESPONSIVE OVERRIDES */
        @media (max-width: 768px) {
            .app-container { 
                flex-direction: column !important; 
                height: auto !important; 
                min-height: 100vh; 
            }
            .sidebar { 
                width: 100% !important; 
                height: auto !important; 
                border-right: none !important; 
                border-bottom: 1px solid rgba(255,255,255,0.1) !important; 
                padding: 1.5rem !important;
            }
            .main-content { 
                width: 100% !important; 
                overflow-y: auto !important; 
            }
            .data-row { 
                flex-wrap: wrap !important; 
                gap: 0.5rem !important; 
                padding: 0.75rem !important; 
            }
            .data-row > div { 
                flex: 1 1 auto !important; 
            }
            .data-row div.flex-1 { 
                min-width: 120px !important; 
            }
            #authScreen { 
                padding: 1rem !important; 
            }
            #authScreen > div { 
                padding: 1.5rem !important; 
            }
            .grid-cols-12 { 
                grid-template-columns: 1fr !important; 
            }
            .md\\:col-span-9, .md\\:col-span-3 { 
                grid-column: span 1 / span 1 !important; 
            }
        }
    """
    
    if '</style>' in content:
        content = content.replace('</style>', f'{mobile_css}\n    </style>')
    else:
        content = content.replace('</head>', f'<style>{mobile_css}</style>\n</head>')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: Mobile responsive patch applied to public/index.html")
    print("\nNow deploy with:")
    print("git add . && git commit -m 'Mobile Responsive UI' && git push origin main")

if __name__ == "__main__":
    apply_mobile_fix()

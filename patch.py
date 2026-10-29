import os

def apply_sidebar_patch():
    file_path = os.path.join('public', 'index.html')
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. ADD CSS for the Sliding Sidebar and Overlay
    sidebar_css = """
        /* SLIDING SIDEBAR SYSTEM */
        .sidebar { 
            position: fixed !important; 
            left: 0; 
            top: 0; 
            bottom: 0; 
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; 
            z-index: 1000 !important;
        }
        .sidebar.closed { 
            transform: translateX(-100%); 
        }
        #sidebarOverlay { 
            position: fixed; 
            inset: 0; 
            background: rgba(0,0,0,0.6); 
            backdrop-filter: blur(4px); 
            z-index: 999; 
            transition: opacity 0.3s ease; 
            pointer-events: none; 
            opacity: 0; 
        }
        #sidebarOverlay.active { 
            pointer-events: auto; 
            opacity: 1; 
        }
        .menu-toggle-btn { 
            cursor: pointer; 
            transition: all 0.2s; 
        }
        .menu-toggle-btn:hover { 
            background: rgba(255,255,255,0.1); 
        }
    """
    content = content.replace('</style>', f'{sidebar_css}\n    </style>')

    # 2. ADD the Overlay div right after <body>
    overlay_html = '<div id="sidebarOverlay" onclick="toggleSidebar()"></div>\n    '
    content = content.replace('<body class="antialiased">', f'<body class="antialiased">\n    {overlay_html}')

    # 3. ADD a Menu Button to the Header
    # We place this inside the <header> tag, before the breadcrumbs
    menu_btn_html = """
                <button onclick="toggleSidebar()" class="menu-toggle-btn p-2 rounded-lg text-slate-400 mr-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                </button>
    """
    content = content.replace('<header class="h-16', f'<header class="h-16{menu_btn_html}')

    # 4. ADD a Close Button (X) inside the Sidebar
    # We place it at the top of the sidebar
    close_btn_html = """
            <div class="flex justify-end mb-4">
                <button onclick="toggleSidebar()" class="p-2 rounded-lg text-slate-500 hover:text-white transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
    """
    content = content.replace('<aside id="sidebar" class="sidebar p-6 w-[280px]">', 
                              f'<aside id="sidebar" class="sidebar p-6 w-[280px] closed">{close_btn_html}')

    # 5. ADD JavaScript logic to control the sidebar
    sidebar_js = """
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            sidebar.classList.toggle('closed');
            overlay.classList.toggle('active');
        }
    """
    content = content.replace('<script>', f'<script>\n    {sidebar_js}')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: Sliding Sidebar patched!")
    print("\nDeploy now:")
    print("git add . && git commit -m 'Add toggleable sidebar' && git push origin main")

if __name__ == "__main__":
    apply_sidebar_patch()

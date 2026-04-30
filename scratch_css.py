import re

with open('src/client/ui/style.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract GLOBAL_STYLESHEET
match = re.search(r'GLOBAL_STYLESHEET\s*=\s*\"\"\"(.*?)\"\"\"', content, re.DOTALL)
if match:
    dark_css = match.group(1)
    
    # Replace colors
    light_css = dark_css
    
    # Backgrounds
    light_css = light_css.replace('#0a0f1e', '#f8fafc') # main bg
    light_css = light_css.replace('#0d1224', '#ffffff') # sidebar/msg bg
    
    # Text
    light_css = light_css.replace('#e2e8f0', '#334155') # base text
    light_css = light_css.replace('#f8fafc', '#0f172a') # title text
    light_css = light_css.replace('#64748b', '#475569') # subtitle
    light_css = light_css.replace('#475569', '#64748b') # muted text
    light_css = light_css.replace('#94a3b8', '#475569') # slightly muted text
    light_css = light_css.replace('#cbd5e1', '#334155') # table text
    light_css = light_css.replace('#1e293b', '#e2e8f0') # tooltip bg
    
    # Accents (Blue -> Orange)
    light_css = light_css.replace('3b82f6', 'f97316')
    light_css = light_css.replace('60a5fa', 'ea580c')
    light_css = light_css.replace('59, 130, 246', '249, 115, 22')
    light_css = light_css.replace('stop:0 #2563eb, stop:1 #3b82f6', 'stop:0 #ea580c, stop:1 #f97316')
    light_css = light_css.replace('stop:0 #1d4ed8, stop:1 #2563eb', 'stop:0 #c2410c, stop:1 #ea580c')
    
    # Borders / Card backgrounds
    light_css = light_css.replace('rgba(13, 18, 36, 0.4)', 'rgba(255, 255, 255, 0.8)') # tab pane
    light_css = light_css.replace('rgba(13, 18, 36, 0.6)', 'rgba(255, 255, 255, 0.9)') # lists
    light_css = light_css.replace('rgba(13, 18, 36, 0.7)', '#ffffff') # cards
    light_css = light_css.replace('rgba(13, 18, 36, 0.8)', '#f1f5f9') # table header
    light_css = light_css.replace('rgba(15, 23, 42, 0.4)', '#f1f5f9') # table alt bg
    light_css = light_css.replace('rgba(15, 23, 42, 0.5)', '#ffffff') # input bg
    light_css = light_css.replace('rgba(15, 23, 42, 0.6)', '#ffffff') # input bg
    light_css = light_css.replace('rgba(15, 23, 42, 0.7)', '#ffffff') # input focus bg
    light_css = light_css.replace('rgba(15, 23, 42, 0.8)', '#e2e8f0') # btn pressed
    
    light_css = light_css.replace('rgba(30, 41, 59, 0.3)', 'rgba(241, 245, 249, 0.8)') # tab hover
    light_css = light_css.replace('rgba(30, 41, 59, 0.4)', 'rgba(226, 232, 240, 0.8)') # ghost hover
    light_css = light_css.replace('rgba(30, 41, 59, 0.7)', '#ffffff') # buttons
    
    light_css = light_css.replace('rgba(51, 65, 85, 0.15)', 'rgba(148, 163, 184, 0.2)')
    light_css = light_css.replace('rgba(51, 65, 85, 0.2)', 'rgba(148, 163, 184, 0.3)')
    light_css = light_css.replace('rgba(51, 65, 85, 0.3)', 'rgba(148, 163, 184, 0.4)')
    light_css = light_css.replace('rgba(51, 65, 85, 0.35)', 'rgba(148, 163, 184, 0.5)')
    light_css = light_css.replace('rgba(51, 65, 85, 0.4)', 'rgba(148, 163, 184, 0.5)')
    light_css = light_css.replace('rgba(51, 65, 85, 0.5)', 'rgba(148, 163, 184, 0.6)')
    light_css = light_css.replace('rgba(51, 65, 85, 0.6)', 'rgba(241, 245, 249, 1.0)') # button hover
    
    light_css = light_css.replace('rgba(71, 85, 105, 0.6)', 'rgba(100, 116, 139, 0.6)')
    light_css = light_css.replace('rgba(71, 85, 105, 0.7)', 'rgba(148, 163, 184, 0.8)')
    
    # Specific fix for QMessageBox text
    light_css = light_css.replace('QMessageBox QLabel {\n    color: #334155;\n    font-size: 13px;\n}', 'QMessageBox QLabel {\n    color: #0f172a;\n    font-size: 13px;\n}')

    new_content = content + '\n\nGLOBAL_LIGHT_STYLESHEET = """' + light_css + '"""\n\n'
    new_content += 'def get_stylesheet(theme: str) -> str:\n'
    new_content += '    return GLOBAL_LIGHT_STYLESHEET if theme == "light" else GLOBAL_STYLESHEET\n'
    
    with open('src/client/ui/style.py', 'w', encoding='utf-8') as f2:
        f2.write(new_content)
    print('Stylesheet generated')
else:
    print('Regex failed')

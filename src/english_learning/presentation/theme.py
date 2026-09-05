"""Central Qt stylesheet palettes."""


def stylesheet(theme: str) -> str:
    dark = theme == "dark"
    background = "#111827" if dark else "#f3f6fa"
    surface = "#1f2937" if dark else "#ffffff"
    text = "#f9fafb" if dark else "#1f2937"
    muted = "#9ca3af" if dark else "#64748b"
    border = "#374151" if dark else "#dbe3ee"
    return f"""
        QWidget {{ background: {background}; color: {text}; font-family: 'Segoe UI', Arial; font-size: 14px; }}
        QFrame#sidebar, QFrame#card {{ background: {surface}; border: 1px solid {border}; border-radius: 12px; }}
        QLabel#title {{ font-size: 26px; font-weight: 700; }}
        QLabel#muted {{ color: {muted}; }}
        QPushButton {{ background: #2563eb; color: white; border: 0; border-radius: 8px; padding: 10px 14px; }}
        QPushButton:hover {{ background: #1d4ed8; }}
        QPushButton:checked {{ background: #1e40af; }}
        QPushButton#nav {{ text-align: left; background: transparent; color: {text}; padding: 12px; }}
        QPushButton#nav:hover, QPushButton#nav:checked {{ background: #2563eb; color: white; }}
        QLineEdit, QComboBox, QSpinBox, QListWidget, QTableWidget, QTextBrowser {{
            background: {surface}; color: {text}; border: 1px solid {border}; border-radius: 7px; padding: 7px;
        }}
        QProgressBar {{ border: 1px solid {border}; border-radius: 6px; text-align: center; }}
        QProgressBar::chunk {{ background: #22c55e; border-radius: 5px; }}
    """

"""Streamlit visual system helpers with clean, student-friendly styling."""

from __future__ import annotations

import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
    <style>
    /* Hide Streamlit default multipage navigation to prevent duplicate menus */
    [data-testid="stSidebarNav"],
    nav[data-testid="stSidebarNav"],
    ul[data-testid="stSidebarNavItems"],
    div[data-testid="stSidebarNavSeparator"],
    header[data-testid="stHeader"] .stNav,
    [data-testid="stTopNav"],
    [data-testid="stHeaderNav"] {
        display: none !important;
    }

    /* Overall layout and typography */
    .block-container {
        padding: 2rem 2.5rem 3.5rem !important;
        max-width: 1350px !important;
    }

    h1 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        letter-spacing: -0.01em !important;
        margin-bottom: 0.25rem !important;
    }

    h2 {
        font-size: 1.45rem !important;
        font-weight: 600 !important;
        margin-top: 1.25rem !important;
        margin-bottom: 0.5rem !important;
    }

    h3 {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.4rem !important;
    }

    h4, h5 {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        margin-top: 0.75rem !important;
        margin-bottom: 0.25rem !important;
    }

    .eyebrow {
        color: #FF4D4D;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }

    .page-subtitle {
        color: #9CA3AF;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        line-height: 1.45;
    }

    /* Clean Card Containers */
    .metric-card {
        background-color: #1A1D24;
        border: 1px solid #2D3748;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.75rem;
    }

    .metric-label {
        color: #9CA3AF;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #F9FAFB;
        margin: 0.2rem 0;
    }

    .metric-note {
        color: #6B7280;
        font-size: 0.72rem;
    }

    .info-card {
        background-color: #1A1D24;
        border: 1px solid #2D3748;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    .info-card h4 {
        margin-top: 0 !important;
        color: #F9FAFB;
    }

    .info-card p {
        color: #9CA3AF;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 0;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #11141A;
        border-right: 1px solid #222732;
    }

    .sidebar-brand {
        padding: 0.5rem 0 1rem;
        border-bottom: 1px solid #222732;
        margin-bottom: 1rem;
    }

    .sidebar-brand b {
        font-size: 1.25rem;
        color: #FFFFFF;
        display: block;
    }

    .sidebar-brand small {
        color: #9CA3AF;
        font-size: 0.75rem;
    }

    .sidebar-footer {
        padding-top: 1rem;
        border-top: 1px solid #222732;
        margin-top: 2rem;
        color: #6B7280;
        font-size: 0.75rem;
        line-height: 1.5;
    }

    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        margin-right: 0.35rem;
    }

    /* Tables & Frames */
    .stDataFrame {
        border-radius: 6px;
        overflow: hidden;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1.25rem 1rem !important;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str, kicker: str = "") -> None:
    """Render a clean, well-proportioned page header."""
    kicker_html = f'<div class="eyebrow">{kicker}</div>' if kicker else ""
    st.markdown(
        f'{kicker_html}<h1>{title}</h1><p class="page-subtitle">{subtitle}</p>',
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, note: str = "") -> None:
    """Render a clean metric summary card."""
    note_html = f'<div class="metric-note">{note}</div>' if note else ""
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div>{note_html}</div>',
        unsafe_allow_html=True,
    )
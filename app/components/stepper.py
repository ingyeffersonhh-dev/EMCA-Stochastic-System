"""
app/components/stepper.py
Shared visual stepper component for page navigation indicators.
"""
import streamlit as st


def render_stepper(steps, current_step=None):
    """
    Render a visual stepper with step indicators.

    Args:
        steps: list of (number, label, completed) tuples, or (number, label)
               tuples (treated as completed).
        current_step: index of the active (non-completed) step, or None.
    """
    html = '<div class="stepper">'
    for i, step in enumerate(steps):
        if len(step) == 3:
            num, label, completed = step
        else:
            num, label = step
            completed = True
        status = "completed" if completed else ("active" if i == current_step else "")
        icon = "✅" if completed else num
        html += f'<div class="stepper-step {status}"><span>{icon}</span><span>{label}</span></div>'
        if i < len(steps) - 1:
            html += '<span class="stepper-arrow">→</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

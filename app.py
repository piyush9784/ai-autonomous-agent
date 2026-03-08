import streamlit as st
import subprocess

st.title("🤖 AI Autonomous Agent")

task = st.text_input("Enter a task for the agent")

if st.button("Run Agent"):

    if task:
        st.write("Running agent...")

        result = subprocess.run(
            ["python", "agent.py", task],
            capture_output=True,
            text=True
        )

        st.text_area("Agent Output", result.stdout, height=300)

    else:
        st.warning("Please enter a task")
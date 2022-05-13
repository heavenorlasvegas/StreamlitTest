import streamlit as st, pandas as pd, numpy as np
"""
график прикольный
"""
x = np.linspace(-8, 8, 1000)
df = pd.DataFrame(dict(y=np.sin(x)))
st.line_chart(df)
import numpy as np
import pandas as pd
import streamlit as st
import mathplotlib.pyplot as plt
with st.echo(code_location='below'):
    """
    график прикольный
    """
    x = np.linspace(-8, 8, 1000)
    df = pd.DataFrame(dict(y=np.sin(x)))
    st.line_chart(df)
    """
    привет нет блин пока
    """
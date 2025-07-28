
import re 
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
def filter_dataframe(df, filters):
    for column, value in filters.items():
        df = df[df[column].isin(value)]
    return df

def filter_dataframeToUpper(df, filters):
    for column, value in filters.items():
        df = df[df[column].str.upper().isin(value)]
    return df

def getColumns(df, columns):
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found in DataFrame: {missing_columns}")
        
        return df[columns]

def is_valid_email(email):
    # Simple regex for validating an email
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None
def loadData(data):
    return pd.read_csv(data)

    df = df.copy()  # Crear una copia para evitar modificar el dataframe original
    df["Diferencia"] = df[value1] - df[value2]
    
    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Definir posiciones en el eje X
    x = np.arange(len(df))

    # Graficar barras apiladas
    bar1 = ax.bar(x, df[value2], color="#1B1C2A", label=value2)
    bar2 = ax.bar(x, df["Diferencia"], bottom=df[value2], color="#E29B47", label="Diferencia")

    # Etiquetas en las barras
    for bars in [bar1, bar2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + height / 2,
                        f'{int(height)}', ha='center', va='center', color='white', fontsize=10)

    # Configurar etiquetas y formato
    ax.set_xticks(x)
    ax.set_xticklabels(df["Centro de trabajo"], rotation=45, ha="right")
    ax.set_yticks(np.arange(0, max(df[value1]) + 10, 10))
    ax.set_yticklabels([f"{int(y)}%" for y in ax.get_yticks()])
    ax.set_ylim(0, max(df[value1]) + 10)

    # Añadir leyenda y ajustar diseño
    ax.legend()
    plt.tight_layout()

    st.pyplot(fig)
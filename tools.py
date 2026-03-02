import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from langchain_core.tools import tool

@tool
def query_sql(sql_query: str):
    """Ejecuta consultas SQL en la tabla 'ventas'. Úsala para obtener datos crudos."""
    conn = sqlite3.connect('sales_data.db')
    try:
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        conn.close()
        return f"Error en el SQL: {str(e)}"

@tool
def generate_chart(data: list, title: str):
    """Crea un gráfico a partir de una lista de datos. Úsala cuando el usuario quiera 'ver', 'graficar' o 'comparar'."""
    df = pd.DataFrame(data)
    if df.empty: return "No hay datos para graficar."
    
    df.plot(kind='bar', x=df.columns[0], y=df.columns[1], legend=False)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = "resultado_grafico.png"
    plt.savefig(path)
    plt.close()
    return f"Gráfico generado exitosamente como '{path}'"

@tool
def export_to_csv(data: list, filename: str = "reporte_ventas.csv"):
    """Guarda los datos en un archivo CSV. Úsala cuando el usuario quiera 'guardar', 'descargar' o 'exportar'."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    return f"Archivo guardado exitosamente como '{filename}'"
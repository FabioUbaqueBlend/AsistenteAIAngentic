import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('sales_data.db')
    data = {
        'id': range(1, 11),
        'vendedor': ['Ana', 'Carlos', 'Ana', 'Beatriz', 'Carlos', 'Ana', 'Beatriz', 'Carlos', 'Ana', 'Carlos'],
        'sede': ['Bogotá', 'Medellín', 'Bogotá', 'Medellín', 'Bogotá', 'Medellín', 'Bogotá', 'Medellín', 'Bogotá', 'Medellín'],
        'producto': ['Laptop', 'Mouse', 'Monitor', 'Laptop', 'Teclado', 'Mouse', 'Monitor', 'Laptop', 'Teclado', 'Mouse'],
        'cantidad': [2, 10, 5, 1, 8, 15, 3, 2, 10, 20],
        'precio': [1200, 25, 300, 1200, 45, 25, 300, 1200, 45, 25],
        'fecha': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10']
    }
    df = pd.DataFrame(data)
    df.to_sql('ventas', conn, if_exists='replace', index=False)
    conn.close()
    print("✅ Base de datos 'sales_data.db' creada correctamente.")

if __name__ == "__main__":
    init_db()
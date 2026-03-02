import os
import boto3
from typing import Annotated, TypedDict
from dotenv import load_dotenv

# Importaciones de LangChain y LangGraph
from langchain_aws import ChatBedrockConverse
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.messages import ToolMessage

# Importamos las herramientas del archivo tools.py
from tools import query_sql, generate_chart, export_to_csv

# 1. Cargar configuración
load_dotenv()

# 2. Configuración de Sesión y Cliente AWS
session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("AWS_REGION")
)
bedrock_client = session.client("bedrock-runtime")

# 3. Definición del Estado del Agente
class AgentState(TypedDict):
    # Usamos una lista de mensajes que se van acumulando
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]

# 4. Inicializar el Modelo (Usando Converse API para mejor manejo de herramientas)
tools = [query_sql, generate_chart, export_to_csv]
model = ChatBedrockConverse(
    model_id=os.getenv("BEDROCK_MODEL_ID"),
    client=bedrock_client,
    temperature=0
).bind_tools(tools)

# 5. Lógica del Nodo del Agente
def call_model(state: AgentState):
    prompt_sistema = SystemMessage(content=(
        "Eres un Agente de Análisis de Ventas experto. "
        "Tu función es traducir preguntas a SQL y ayudar con gráficos o archivos.\n"
        "REGLAS:\n"
        "1. Si el usuario pide datos, usa 'query_sql'.\n"
        "2. Si pide visualización, usa 'generate_chart'.\n"
        "3. Si pide guardar, usa 'export_to_csv'.\n"
        "4. NO des explicaciones largas antes de usar una herramienta. "
        "Si vas a usar una herramienta, simplemente haz la llamada."
    ))
    
    # Aseguramos que el SystemMessage esté al inicio
    chain = [prompt_sistema] + state['messages']
    response = model.invoke(chain)
    
    # Retornamos como lista para que el 'Annotated' lo sume al estado
    return {"messages": [response]}

# 6. Construcción del Grafo de LangGraph
workflow = StateGraph(AgentState)

# Añadimos los nodos
workflow.add_node("agent", call_model)
workflow.add_node("action", ToolNode(tools))

# Definimos el punto de entrada
workflow.set_entry_point("agent")

# Función de decisión (Router)
def should_continue(state: AgentState):
    last_message = state['messages'][-1]
    # Si el modelo hizo una llamada a herramientas (tool_calls), vamos a 'action'
    if last_message.tool_calls:
        return "action"
    # Si no, terminamos la respuesta al usuario
    return END

# Añadimos las conexiones (Edges)
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("action", "agent")

# Compilamos el Grafo
app = workflow.compile()

# 7. Interfaz de Usuario por Consola
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 AGENTE DE VENTAS (BEDROCK + LANGGRAPH)")
    print("="*50)
    print("Sugerencia: '¿Quién vendió más?' o 'Haz un gráfico de ventas por sede'")
    
    # Mantener una sesión de mensajes
    session_messages = []
    
    while True:
        user_input = input("\n👤 Usuario: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("Hasta luego!")
            break
            
        # Ejecutamos el flujo
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        # El stream nos permite ver qué nodo se está ejecutando
        for output in app.stream(inputs, config={"recursion_limit": 15}):
            for key, value in output.items():
                if key == "agent":
                    msg = value['messages'][-1]
                    if msg.content:
                        print(f"\n🤖 Agente: {msg.content}")
                elif key == "action":
                    print("⚙️  [Sistema] Ejecutando herramientas...")
"""
SIPAC - Sistema Interactivo de Procesos con LangGraph
Implementación completa usando arquitectura de grafos de estados
"""

from typing import TypedDict, List, Literal, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
#from langchain_google_generative_ai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import operator
import json
from pathlib import Path

load_dotenv()

# ============================================================================
# DEFINICIÓN DE CATÁLOGOS Y DATOS DE REFERENCIA
# ============================================================================

GIA_CATALOG = {
    1: "Modelo Productivo / Ejecución del Servicio",
    2: "Modelo Comercial o de Clientes",
    3: "Modelo de Oferta y Diversificación de Servicios / Innovación",
    4: "Modelo de Expansión Geográfica Internacional",
    5: "Modelo de RRHH / Desarrollo Profesional / Principios y Valores",
    6: "Modelo Retributivo y de Propiedad",
    7: "Modelo de Marca",
    8: "Modelo de Relaciones Institucionales y Networking de Alto Nivel/Stakeholders",
    9: "Modelo de Organización y Procesos",
    10: "Modelo de Estrategia de la Compañía",
    11: "Modelo de Gestión del Conocimiento Organizativo",
}

CI_TYPES = {
    1: [
        "Capital humano",
        "Capital organizativo",
        "Capital tecnológico",
        "Capital de negocio",
        "Capital social",
    ],
    2: [
        "Capital humano",
        "Capital organizativo",
        "Capital de negocio",
        "Capital social",
        "Capital de emprendimiento e innovación",
    ],
    3: [
        "Capital humano",
        "Capital organizativo",
        "Capital tecnológico",
        "Capital de negocio",
        "Capital de emprendimiento e innovación",
    ],
    4: [
        "Capital organizativo",
        "Capital de negocio",
        "Capital de emprendimiento e innovación",
    ],
    5: [
        "Capital humano",
        "Capital organizativo",
        "Capital tecnológico",
        "Capital de negocio",
        "Capital social",
        "Capital de emprendimiento e innovación",
    ],
    6: [
        "Capital humano",
        "Capital organizativo",
        "Capital tecnológico",
        "Capital de negocio",
        "Capital de emprendimiento e innovación",
    ],
    7: ["Capital humano", "Capital de negocio", "Capital social"],
    8: ["Capital organizativo", "Capital de negocio", "Capital social"],
    9: [
        "Capital organizativo",
        "Capital social",
        "Capital de emprendimiento e innovación",
    ],
    10: [
        "Capital de negocio",
        "Capital social",
        "Capital de emprendimiento e innovación",
    ],
    11: [
        "Capital humano",
        "Capital organizativo",
        "Capital tecnológico",
        "Capital de emprendimiento e innovación",
    ],
}

RESULTS_DIR = Path(__file__).parent.parent / "results"

MAX_RETRIES = 5
# ============================================================================
# DEFINICIÓN DEL ESTADO
# ============================================================================


class SipacState(TypedDict):
    """Estado completo del proceso SIPAC"""

    # Control de flujo
    current_step: int
    messages: Annotated[List[BaseMessage], operator.add]
    conversation_history: Annotated[List[dict], operator.add]

    # Inputs del proceso
    objetivo_negocio: str
    requisitos_de_negocio: List[str]
    procesos: List[str]
    tipo_generico: List[int]  # IDs del GIA_CATALOG
    activo_especifico: List[str]
    importancia_activo: List[int]  # Escala 1-5
    tipo_CI_Intellectus: List[str]  # Tipos de capital intelectual

    # Control de validación
    validation_error: str
    retry_count: int

    # Outputs
    analysis_results: dict
    completed: bool


# ============================================================================
# DEFINICIÓN DE PASOS
# ============================================================================

STEPS = [
    {
        "key": "objetivo_negocio",
        "title": "Objetivo de Negocio",
        "description": """
El objetivo de negocio es la meta principal que la organización desea alcanzar.
Debe ser específico, medible y orientado a resultados.

**Ejemplos:**
- "Aumentar la cuota de mercado en un 15% en el sector de tecnología educativa"
- "Ampliar el alcance de la empresa para poder llegar a más clientes"
- "Reducir costos operativos mediante automatización de procesos"
- "Lanzar un nuevo producto al mercado internacional"
        """,
        "prompt": "¿Cuál es el objetivo principal de negocio que deseas alcanzar?",
        "type": "string",
        "required": True,
        "min_length": 10,
    },
    {
        "key": "requisitos_de_negocio",
        "title": "Requisitos de Negocio",
        "description": """
Los requisitos de negocio son las condiciones o capacidades específicas necesarias
para lograr el objetivo planteado. Deben ser concretos y accionables.

**Ejemplos:**
- "Implementar un sistema CRM para gestión de clientes"
- "Ampliar modelo de negocio (de tienda física a tienda online)"
- "Contratar equipo especializado en inteligencia artificial"
- "Establecer alianzas con distribuidores locales"

**Formato:** Lista separada por comas o saltos de línea
        """,
        "prompt": "¿Qué requisitos de negocio necesitas cumplir? (separa múltiples requisitos por comas)",
        "type": "list",
        "required": True,
        "min_items": 1,
    },
    {
        "key": "procesos",
        "title": "Procesos Involucrados",
        "description": """
Los procesos son las actividades o flujos de trabajo que se verán afectados
o que necesitan implementarse para cumplir los requisitos.

**Ejemplos:**
- "Diversificación de servicios"
- "Digitalización de la cadena de suministro"
- "Mejora del almacenamiento del conocimiento"
- "Optimización del proceso de ventas"
- "Automatización de reporting financiero"

**Formato:** Lista separada por comas o saltos de línea
        """,
        "prompt": "¿Qué procesos están involucrados o necesitan modificarse? (separa múltiples procesos por comas)",
        "type": "list",
        "required": True,
        "min_items": 1,
    },
    {
        "key": "activos_conjunto",
        "title": "Identificación de Activos Intangibles",
        "description": """
Para cada activo intangible necesario, debes proporcionar 3 datos:

1. **Tipo Genérico (GIA):** Categoría del activo según el catálogo GIA
2. **Activo Específico:** Descripción concreta del activo
3. **Nivel de Importancia:** Escala 1-5 (1=Baja, 5=Crítica)

**Catálogo GIA disponible:**
{gia_catalog}

**Tipos de Capital Intelectual:**
{ci_types}

**Ejemplo de respuesta:**
```
[
  {{
    "tipo_generico": 3,
    "activo_especifico": "Creación de tienda online",
    "importancia": 5,
    "tipo_ci": "capital tecnológico"
  }},
  {{
    "tipo_generico": 11,
    "activo_especifico": "Base de datos de conocimiento",
    "importancia": 4,
    "tipo_ci": "capital organizativo"
  }}
]
```
        """,
        "prompt": "Describe los activos intangibles necesarios en formato JSON (lista de objetos con tipo_generico, activo_especifico, importancia, tipo_ci)",
        "type": "json_array",
        "required": True,
        "min_items": 1,
    },
]


# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================


def validate_string(value: str, min_length: int = 1) -> tuple[bool, str]:
    """Valida que sea un string no vacío con longitud mínima"""
    if not isinstance(value, str):
        return False, "Debe ser texto"
    if len(value.strip()) < min_length:
        return False, f"Debe tener al menos {min_length} caracteres"
    return True, ""


def validate_list(value: str, min_items: int = 1) -> tuple[bool, str, List[str]]:
    """Valida y convierte una lista de items separados por comas"""
    if not isinstance(value, str):
        return False, "Debe ser texto", []

    # Intentar separar por comas o saltos de línea
    items = [
        item.strip() for item in value.replace("\n", ",").split(",") if item.strip()
    ]

    if len(items) < min_items:
        return False, f"Debe contener al menos {min_items} elemento(s)", []

    return True, "", items


def validate_activos_json(value: str) -> tuple[bool, str, dict]:
    """Valida el JSON de activos intangibles"""
    try:
        # Limpiar y parsear JSON
        data = json.loads(value.strip())

        if not isinstance(data, list):
            return False, "Debe ser una lista de objetos JSON", {}

        if len(data) == 0:
            return False, "Debe contener al menos un activo", {}

        # Validar cada activo
        activos_validados = []

        for i, activo in enumerate(data):
            if not isinstance(activo, dict):
                return False, f"El elemento {i + 1} debe ser un objeto JSON", {}

            # Validar tipo_generico
            if "tipo_generico" not in activo:
                return False, f"El activo {i + 1} debe tener 'tipo_generico'", {}

            gia_id = activo["tipo_generico"]
            if not isinstance(gia_id, int) or gia_id not in GIA_CATALOG:
                return (
                    False,
                    f"tipo_generico {gia_id} no válido. Debe ser uno de: {list(GIA_CATALOG.keys())}",
                    {},
                )

            # Validar activo_especifico
            if "activo_especifico" not in activo:
                return False, f"El activo {i + 1} debe tener 'activo_especifico'", {}

            if (
                not isinstance(activo["activo_especifico"], str)
                or len(activo["activo_especifico"].strip()) < 5
            ):
                return (
                    False,
                    f"activo_especifico del activo {i + 1} debe ser texto de al menos 5 caracteres",
                    {},
                )

            # Validar importancia
            if "importancia" not in activo:
                return False, f"El activo {i + 1} debe tener 'importancia'", {}

            imp = activo["importancia"]
            if not isinstance(imp, int) or imp < 1 or imp > 5:
                return (
                    False,
                    f"importancia del activo {i + 1} debe ser un número entre 1 y 5",
                    {},
                )
            
            ci_type_input = activo["tipo_ci"].strip()

            valid_ci_types = CI_TYPES.get(gia_id, [])
            valid_ci_map = {t.lower(): t for t in valid_ci_types}

            if ci_type_input.lower() not in valid_ci_map:
                return (
                    False,
                    f"En el activo {i + 1}: tipo_ci '{ci_type_input}' no válido para GIA {gia_id}. Debe ser uno de: {valid_ci_types}",
                    {},
                )
            
            ci_type = valid_ci_map[ci_type_input.lower()]

            # Agregar a lista de activos
            activos_validados.append(
                {
                    "tipo_generico": gia_id,
                    "activo_especifico": activo["activo_especifico"].strip(),
                    "importancia_activo": imp,
                    "tipo_CI_Intellectus": ci_type,
                }
            )

        return True, "", {"activos": activos_validados}

    except json.JSONDecodeError as e:
        return False, f"JSON inválido: {str(e)}", {}
    except Exception as e:
        return False, f"Error al procesar: {str(e)}", {}


# ============================================================================
# NODOS DEL GRAFO
# ============================================================================


def create_step_prompt(step_index: int, state: SipacState) -> str:
    """Crea el prompt del sistema para un paso específico"""
    step = STEPS[step_index]

    # Formatear descripción con catálogo si es necesario
    description = step["description"]
    format_kwargs = {}
    if "{gia_catalog}" in description:
        format_kwargs["gia_catalog"] = "\n".join(
            [f"  {id}: {name}" for id, name in GIA_CATALOG.items()]
        )
    if "{ci_types}" in description:
        format_kwargs["ci_types"] = "\n".join(
            [f"  {id}: {', '.join(types)}" for id, types in CI_TYPES.items()]
        )
    
    if format_kwargs:
        description = description.format(**format_kwargs)

    system_prompt = f"""Eres un asistente experto en análisis de activos intangibles y transformación digital. Vas a ayudar a una empresa a realizar un análisis sobre esta misma para realizar un plan de transformación digital.

# PASO {step_index + 1} de {len(STEPS)}: {step["title"]}

{description}

## INSTRUCCIONES
- Proporciona ÚNICAMENTE el valor solicitado
- Sigue EXACTAMENTE el formato indicado en los ejemplos
- No añadas explicaciones adicionales
- Si son múltiples valores, usa el formato especificado (comas, JSON, etc.)
"""

    if state.get("validation_error"):
        system_prompt += f"""

## ⚠️ ERROR EN INTENTO ANTERIOR
{state["validation_error"]}

Por favor, corrige tu respuesta siguiendo el formato y las reglas especificadas.
"""

    return system_prompt


def agent_input_node(state: SipacState) -> dict:
    """Nodo que solicita input al LLM para el paso actual"""
    llm = ChatOllama(model="qwen3:8b", temperature=0)
    #llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)

    step_index = state["current_step"]

    if step_index >= len(STEPS):
        return {}

    step = STEPS[step_index]

    # Crear prompt del sistema,
    system_prompt = create_step_prompt(step_index, state)

    # Construir mensajes
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=step["prompt"]),
    ]

    # Añadir contexto de reintentos
    if state.get("validation_error"):
        messages.append(
            HumanMessage(
                content=f"Intento anterior rechazado. Error: {state['validation_error']}"
            )
        )

    # Invocar LLM
    response = llm.invoke(messages)

    return {
        "messages": [response],
        "conversation_history": [
            {
                "step": step_index,
                "step_name": step["title"],
                "prompt": step["prompt"],
                "response": response.content,
            }
        ],
    }


def validation_node(state: SipacState) -> dict:
    """Nodo que valida la respuesta del agente"""
    step_index = state["current_step"]
    step = STEPS[step_index]

    if not state.get("messages"):
        return {
            "validation_error": "No hay respuesta del agente",
            "retry_count": state.get("retry_count", 0) + 1,
        }

    # Obtener última respuesta
    last_message = state["messages"][-1]

    if isinstance(last_message.content, list):
        raw_response = " ".join(
            str(part) if not isinstance(part, dict) else part.get("text", "")
            for part in last_message.content
        ).strip()
    else:
        raw_response = last_message.content.strip()

    # Validar según el tipo de pasoº
    if step["type"] == "string":
        is_valid, error = validate_string(raw_response, step.get("min_length", 1))
        if is_valid:
            return {
                step["key"]: raw_response,
                "validation_error": "",
                "retry_count": 0,
                "current_step": step_index + 1,
            }
        else:
            return {
                "validation_error": error,
                "retry_count": state.get("retry_count", 0) + 1,
            }

    elif step["type"] == "list":
        is_valid, error, items = validate_list(raw_response, step.get("min_items", 1))
        if is_valid:
            return {
                step["key"]: items,
                "validation_error": "",
                "retry_count": 0,
                "current_step": step_index + 1,
            }
        else:
            return {
                "validation_error": error,
                "retry_count": state.get("retry_count", 0) + 1,
            }

    elif step["type"] == "json_array":
        is_valid, error, result = validate_activos_json(raw_response)
        if is_valid:
            # Desempaquetar la lista de activos en las listas individuales del estado
            activos = result["activos"]
            return {
                "tipo_generico": [a["tipo_generico"] for a in activos],
                "activo_especifico": [a["activo_especifico"] for a in activos],
                "importancia_activo": [a["importancia_activo"] for a in activos],
                "tipo_CI_Intellectus": [a["tipo_CI_Intellectus"] for a in activos],
                "validation_error": "",
                "retry_count": 0,
                "current_step": step_index + 1,
            }
        else:
            return {
                "validation_error": error,
                "retry_count": state.get("retry_count", 0) + 1,
            }

    return {
        "validation_error": "Tipo de validación no implementado",
        "retry_count": state.get("retry_count", 0) + 1,
    }


def analysis_node(state: SipacState) -> dict:
    """Nodo que realiza el análisis final de los datos recopilados"""

    analysis = {
        "resumen_inputs": {
            "objetivo": state.get("objetivo_negocio", ""),
            "num_requisitos": len(state.get("requisitos_de_negocio", [])),
            "num_procesos": len(state.get("procesos", [])),
            "num_activos": len(state.get("tipo_generico", [])),
        },
        "activos_identificados": [],
        "metricas": {},
        "recomendaciones": [],
    }

    # Analizar cada activo
    tipo_generico = state.get("tipo_generico", [])
    activo_especifico = state.get("activo_especifico", [])
    importancia = state.get("importancia_activo", [])
    tipo_ci = state.get("tipo_CI_Intellectus", [])

    for i in range(len(tipo_generico)):
        activo_data = {
            "id": i + 1,
            "categoria_gia": {
                "id": tipo_generico[i],
                "nombre": GIA_CATALOG.get(tipo_generico[i], "Desconocido"),
            },
            "descripcion": activo_especifico[i],
            "importancia": importancia[i],
            "tipo_capital_intelectual": tipo_ci[i],
        }
        analysis["activos_identificados"].append(activo_data)

    # Calcular métricas
    if importancia:
        analysis["metricas"]["importancia_promedio"] = round(
            sum(importancia) / len(importancia), 2
        )
        analysis["metricas"]["activos_criticos"] = sum(
            1 for imp in importancia if imp >= 4
        )
        analysis["metricas"]["activos_alta_prioridad"] = sum(
            1 for imp in importancia if imp == 5
        )

    # Distribución por tipo de capital intelectual
    ci_distribution = {}
    for ci in tipo_ci:
        ci_distribution[ci] = ci_distribution.get(ci, 0) + 1
    analysis["metricas"]["distribucion_capital_intelectual"] = ci_distribution

    # Distribución por categoría GIA
    gia_distribution = {}
    for gia_id in tipo_generico:
        gia_name = GIA_CATALOG.get(gia_id, "Desconocido")
        gia_distribution[gia_name] = gia_distribution.get(gia_name, 0) + 1
    analysis["metricas"]["distribucion_gia"] = gia_distribution

    # Generar recomendaciones
    if analysis["metricas"].get("activos_criticos", 0) > len(tipo_generico) * 0.5:
        analysis["recomendaciones"].append(
            "Más del 50% de tus activos son críticos. Considera priorizar inversiones en protección y gestión de riesgos."
        )

    if ci_distribution.get("capital tecnológico", 0) > len(tipo_ci) * 0.6:
        analysis["recomendaciones"].append(
            "Alta concentración en capital tecnológico. Evalúa balancear con capital humano y organizativo."
        )

    if len(state.get("requisitos_de_negocio", [])) > len(tipo_generico):
        analysis["recomendaciones"].append(
            "Tienes más requisitos que activos identificados. Considera si faltan activos intangibles por identificar."
        )

    return {
        "analysis_results": analysis,
        "completed": True,
        "messages": [
            AIMessage(
                content=f"Análisis completado exitosamente. Se identificaron {len(tipo_generico)} activos intangibles."
            )
        ],
    }


def error_node(state: SipacState) -> dict:
    """Nodo de manejo de errores cuando se exceden los reintentos"""
    step_index = state.get("current_step", 0)
    step_name = STEPS[step_index]["title"] if step_index < len(STEPS) else "Desconocido"

    error_message = {
        "error": "MAX_RETRIES_EXCEEDED",
        "step": step_name,
        "step_index": step_index,
        "last_error": state.get("validation_error", ""),
        "retry_count": state.get("retry_count", 0),
    }

    return {
        "analysis_results": error_message,
        "completed": False,
        "messages": [
            AIMessage(
                content=f"Error: Se excedieron los reintentos en el paso '{step_name}'"
            )
        ],
    }


# ============================================================================
# FUNCIONES DE REINTENTO
# ============================================================================


def should_retry(state: SipacState) -> Literal["agent", "analysis", "error"]:
    """Decide si reintentar, continuar al siguiente paso o terminar con error"""
    max_retries = MAX_RETRIES
    retry_count = state.get("retry_count", 0)

    # Si hay error de validación
    if state.get("validation_error"):
        if retry_count >= max_retries:
            return "error"
        return "agent"

    # Si no hay error, verificar si completamos todos los pasos
    if state.get("current_step", 0) >= len(STEPS):
        return "analysis"

    return "agent"


# ============================================================================
# CONSTRUCCIÓN DEL GRAFO
# ============================================================================


def create_sipac_graph() -> CompiledStateGraph:
    """Crea y configura el grafo completo de SIPAC"""

    workflow = StateGraph(SipacState)

    # Añadir nodos
    workflow.add_node("agent", agent_input_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("error", error_node)

    # Punto de entrada
    workflow.set_entry_point("agent")

    # Flujo principal: agent -> validation
    workflow.add_edge("agent", "validation")

    # Desde validation, decidir qué hacer
    workflow.add_conditional_edges(
        "validation",
        should_retry,
        {
            "agent": "agent",  # Reintentar el paso actual
            "analysis": "analysis",  # Ir a análisis final
            "error": "error",  # Error fatal
        },
    )

    # Nodos finales
    workflow.add_edge("analysis", END)
    workflow.add_edge("error", END)

    return workflow.compile()


# ============================================================================
# FUNCIÓN PRINCIPAL DE EJECUCIÓN
# ============================================================================


def run_sipac(initial_state: dict = {}, stream: bool = True) -> dict:
    """
    Ejecuta el flujo completo de SIPAC

    Args:
        initial_state: Estado inicial (opcional, para testing)
        stream: Si True, imprime el progreso paso a paso

    Returns:
        Estado final con los resultados del análisis
    """
    graph = create_sipac_graph()

    # Estado inicial por defecto
    if initial_state == {}:
        initial_state = {
            "current_step": 0,
            "messages": [],
            "conversation_history": [],
            "validation_error": "",
            "retry_count": 0,
            "completed": False,
        }

    if stream:
        print("=" * 70)
        print("SIPAC - Sistema Interactivo de Procesos con LangGraph")
        print("=" * 70)
        print(f"\nIniciando proceso con {len(STEPS)} pasos...\n")

        final_state = {}
        for step_output in graph.stream(initial_state):
            node_name = list(step_output.keys())[0]
            node_state = step_output[node_name]

            # Mostrar progreso
            if node_name == "agent":
                step_idx = node_state["conversation_history"][0]["step"]
                if step_idx < len(STEPS):
                    print(f"\n{'─' * 70}")
                    print(
                        f" PASO {step_idx + 1}/{len(STEPS)}: {STEPS[step_idx]['title']}"
                    )
                    print(f"{'─' * 70}")

            # Mostrar respuesta del agente
            if node_state.get("messages"):
                last_msg = node_state["messages"][-1]
                if isinstance(last_msg, AIMessage):
                    print(
                        f"\n Respuesta: {last_msg.content[:200]}{'...' if len(last_msg.content) > 200 else ''}"
                    )

            # Mostrar errores de validación
            if node_state.get("validation_error"):
                print(f"\n  Error de validación: {node_state['validation_error']}")
                print(f"   Reintento {node_state.get('retry_count', 0)}/{MAX_RETRIES}")

            final_state = node_state

        return final_state
    else:
        return graph.invoke(initial_state)


if __name__ == "__main__":
    # Ejecutar SIPAC
    final_state = run_sipac(stream=True)

    # Mostrar resultados
    print("\n" + "=" * 70)
    print("RESULTADOS FINALES")
    print("=" * 70)

    if final_state.get("completed"):
        print("\n Proceso completado exitosamente\n")
        print(
            json.dumps(
                final_state.get("analysis_results", {}), indent=2, ensure_ascii=False
            )
        )
    else:
        print("\n Proceso terminó con errores\n")
        print(
            json.dumps(
                final_state.get("analysis_results", {}), indent=2, ensure_ascii=False
            )
        )

    # Exportar resultados

    results_path = Path(RESULTS_DIR)
    results_path.mkdir(exist_ok=True)
    output_file = results_path / "sipac_results.json"

    if output_file.exists():
        counter = 1
        while (results_path / f"sipac_results_{counter}.json").exists():
            counter += 1
        output_file = results_path / f"sipac_results_{counter}.json"

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "inputs": {
                    "objetivo_negocio": final_state.get("objetivo_negocio"),
                    "requisitos_de_negocio": final_state.get("requisitos_de_negocio"),
                    "procesos": final_state.get("procesos"),
                },
                "activos": {
                    "tipo_generico": final_state.get("tipo_generico"),
                    "activo_especifico": final_state.get("activo_especifico"),
                    "importancia_activo": final_state.get("importancia_activo"),
                    "tipo_CI_Intellectus": final_state.get("tipo_CI_Intellectus"),
                },
                "analysis": final_state.get("analysis_results"),
                "conversation_history": final_state.get("conversation_history", []),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n Resultados exportados a: {output_file}")

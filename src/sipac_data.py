import json
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

# Catálogo centralizado de GIA
GIA_CATALOG: Dict[int, str] = {
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


class Step:
    """
    Define la estructura de un paso en el proceso de recolección de datos.
    """

    def __init__(
        self,
        id: int,
        key: str,
        title: str,
        documentation: Union[str, Callable[[dict], str]],
        prompt: Union[str, Callable[[dict], str]],
        examples: str,
        validator: Optional[
            Union[Callable[[str], bool], Callable[[str, dict], bool]]
        ] = None,
        cast_func: Callable[[str], Any] = str,
    ):
        self.id = id
        self.key = key
        self.title = title
        self.documentation = documentation
        self.prompt = prompt
        self.examples = examples
        self.validator = validator
        self.cast_func = cast_func


def generate_gia_table() -> str:
    """Genera la tabla Markdown para la documentación del paso 3."""
    table = "| GIA | Descripción |\n|-----|-------------|\n"
    for gid, desc in GIA_CATALOG.items():
        table += f"| {gid:<3} | {desc} |\n"
    return table


def get_dynamic_asset_documentation(
    data: dict, include_importance: bool = False
) -> str:
    selected_gias = data.get("tipo_generico", [])
    specific_assets = data.get("activo_especifico", [])
    importance_scores = data.get("importancia_activo", [])

    if not selected_gias:
        return "No se seleccionaron GIAs en el paso anterior."

    doc = ""
    for i, gia_id in enumerate(selected_gias):
        gia_desc = GIA_CATALOG.get(gia_id, "Desconocido")
        specific_asset = (
            specific_assets[i] if i < len(specific_assets) else "No especificado"
        )

        doc += f"{i + 1}. [GIA {gia_id}] {gia_desc}\n"
        doc += f"   Activo específico: {specific_asset}\n"

        if include_importance and i < len(importance_scores):
            doc += f"   Importancia: {importance_scores[i]}/5\n"

        doc += "\n"

    return doc


def get_step5_documentation(data: dict) -> str:
    header = (
        "Para cada tipo de activo genérico intangible (GIA) seleccionado en el paso 3, "
        "se debe identificar el activo específico intangible de la empresa.\n\n"
        "LISTA DE GIA SELECCIONADOS (en orden):\n"
        "=======================================\n"
    )

    asset_list = ""
    for i, gia_id in enumerate(data.get("tipo_generico", [])):
        desc = GIA_CATALOG.get(gia_id, "Desconocido")
        asset_list += f"{i + 1}. [GIA {gia_id}] {desc}\n"

    return (
        header + asset_list
        if asset_list
        else "No se seleccionaron GIAs en el paso anterior."
    )


def get_step6_documentation(data: dict) -> str:
    header = (
        "Especifica la importancia de cada activo específico intangible identificado en el paso 5, "
        "en un rango del 1 al 5 (1 = poca importancia, 5 = mucha importancia), en base a su impacto "
        "en la consecución del objetivo de negocio.\n\n"
        "ACTIVOS ESPECÍFICOS A EVALUAR:\n"
        "================================\n\n"
    )

    return header + get_dynamic_asset_documentation(data)


def load_gia_ci_mapping() -> Dict[str, list[str]]:
    mapping_path = Path(__file__).parent.parent / "docs" / "mapeo_gia_ci.json"
    with open(mapping_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_step7_documentation(data: dict) -> str:
    header = (
        "Para cada activo específico intangible, identifica el tipo de Capital Intelectual (CI) "
        "según el modelo Intellectus que mejor lo representa.\n\n"
    )

    mapping = load_gia_ci_mapping()
    selected_gias = data.get("tipo_generico", [])

    if not selected_gias:
        return header + "No se seleccionaron GIAs en el paso anterior."

    header += "ACTIVOS ESPECÍFICOS Y CI APPLICABLES:\n"
    header += "======================================\n\n"

    asset_docs = get_dynamic_asset_documentation(data, include_importance=True)

    mapping_section = "\nMAPEO GIA → CAPITAL INTELECTUAL:\n"
    mapping_section += "==================================\n\n"

    processed_gias = set()
    for gia_id in selected_gias:
        if gia_id in processed_gias:
            continue
        processed_gias.add(gia_id)

        gia_desc = GIA_CATALOG.get(gia_id, "Desconocido")
        ci_types = mapping.get(str(gia_id), [])

        mapping_section += f"GIA {gia_id}: {gia_desc}\n"
        mapping_section += "  → Tipos de CI aplicables:\n"
        for ci_type in ci_types:
            mapping_section += f"     • {ci_type}\n"
        mapping_section += "\n"

    return header + asset_docs + mapping_section


def validate_ci_for_gias(ci_input: str, data: dict) -> bool:
    ci_list = [s.strip() for s in ci_input.split(",")]
    selected_gias = data.get("tipo_generico", [])

    if len(ci_list) != len(selected_gias):
        return False

    mapping = load_gia_ci_mapping()

    for _, (ci_type, gia_id) in enumerate(zip(ci_list, selected_gias)):
        # Normalizar a minusculas los valores validos del mapping para comparar
        valid_ci_types = [v.lower() for v in mapping.get(str(gia_id), [])]
        if ci_type not in valid_ci_types:
            return False

    return True


# ==============================================================================
# DEFINICIÓN DEL FLUJO DE DATOS
# ==============================================================================

SIPAC_STEPS = [
    Step(
        id=1,
        key="objetivo_negocio",
        title="OBJETIVO DEL NEGOCIO",
        documentation="Específica el objetivo de negocio de la empresa cliente para la que quiere realizarse el plan de DX. \n Se conciso y claro, no más de 10 palabras en la medida de lo posible.",
        prompt="Introduce el objetivo del negocio",
        examples="Ampliar el alcance de la empresa para poder llegar a más clientes",
    ),
    Step(
        id=2,
        key="requisitos_de_negocio",
        title="REQUISITOS DEL NEGOCIO",
        documentation="Especifica los requisitos de negocio clave que están relacionados con el objetivo de negocio proporcionado en el paso 1. \n Ten en cuenta que el objetivo de negocio puede estar relacionado con varios requisitos de negocio. \n Proporciona una lista de requisitos relacionados con el objetivo de negocio separados por comas.",
        prompt="Introduce los requisitos del negocio, separados por comas",
        examples="Ampliar modelo de negocio (de tienda física a tienda online, ser distribuidor y ofrecer servicio de catas en tienda), requisito 2, requisito 3",
        cast_func=lambda x: [s.strip() for s in x.split(",")],
    ),
    Step(
        id=3,
        key="procesos",
        title="PROCESOS",
        documentation="Se deben de identificar los procesos de la empresa que pueden ayudar a obtener el objetivo de negocio fijado en el paso 1.",
        prompt="Introduce los procesos de la empresa relacionados con el objetivo de negocio, separados por comas",
        examples="Diversificación de servicios, Mejora del almacenamiento del conocimiento, Proceso 3",
        cast_func=lambda x: [s.strip() for s in x.split(",")],
    ),
    Step(
        id=4,
        key="tipo_generico",
        title="TIPO DE ACTIVO GENÉRICO INTANGIBLE (GIA)",
        documentation=f"""
Se deben de identificar los tipos de activos genéricos intangibles (GIA) que hacen cuello de botella y que harían palanca para obtener el objetivo de negocio fijado en el paso 1, si se han detectado varios activos intangibles del mismo tipo, deben de repetirse en el listado el tipo según el número de apariciones.
Los tipos de activos deben de seleccionarse de la siguiente lista:

{generate_gia_table()}
""",
        prompt="Introduce los números de los GIA seleccionados, separados por comas (ej: 1, 3)",
        examples="3, 3, 11",
        validator=lambda x: all(
            part.strip().isdigit() and int(part.strip()) in GIA_CATALOG
            for part in x.split(",")
        ),
        cast_func=lambda x: [int(part.strip()) for part in x.split(",")],
    ),
    Step(
        id=5,
        key="activo_especifico",
        title="ACTIVO ESPECÍFICO INTANGIBLE",
        documentation=get_step5_documentation,
        prompt="Introduce los activos específicos intangibles, separados por comas, en el mismo orden que los GIA listados arriba",
        examples="Creación de tienda online, Formulario para las ventas online, Creación de un repositorio/base de datos para almacenar el conocimiento.",
        # Valida que el número de activos introducidos coincida con los GIA seleccionados
        validator=lambda x, data: len(x.split(","))
        == len(data.get("tipo_generico", [])),
        cast_func=lambda x: [s.strip() for s in x.split(",")],
    ),
    Step(
        id=6,
        key="importancia_activo",
        title="IMPORTANCIA DEL ACTIVO ESPECÍFICO INTANGIBLE",
        documentation=get_step6_documentation,
        prompt="Introduce la importancia (1-5) de cada activo, en orden, separados por comas",
        examples="5, 4, 3",
        validator=lambda x, data: (
            all(
                part.strip().isdigit() and 1 <= int(part.strip()) <= 5
                for part in x.split(",")
            )
            and len(x.split(",")) == len(data.get("activo_especifico", []))
        ),
        cast_func=lambda x: [int(part.strip()) for part in x.split(",")],
    ),
    Step(
        id=7,
        key="tipo_CI_Intellectus",
        title="TIPO DE CI INTELLECTUS",
        documentation=get_step7_documentation,
        prompt="Introduce los tipos de CI Intellectus para cada GIA, separados por comas",
        examples="Capital humano, Capital tecnológico, Capital de negocio",
        validator=lambda x, data: validate_ci_for_gias(x, data),
        cast_func=lambda x: [s.strip() for s in x.split(",")],
    ),
]

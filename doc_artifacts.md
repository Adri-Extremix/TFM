# Artifacts Documentation

Se deben de identificar cuáles son los activos intangibles de la empresa que hacen cuello de botella y que harían palanca para obtener el objetivo fijado en el plan de DX.

El resultado esperado debe de estar en formato JSON, siguiendo la estructura que se detalla a continuación:

# Activo Intangible
- **Type**: Array of Objects
- **Depends on**: Objetivo_Negocio
- **Name**: Activos_Intangibles
- **Description**: Se deben de generar una lista de activos intangibles, cada uno con las características siguientes:

## Tipo Genérico de Activo Intangible (GIA)
- **Type**: String
- **Depends on**: Objetivo_Negocio
- **Name**: TIPO_GIA
- **Validation Rule**: El `TIPO_GIA` debe de ser uno de los valores permitidos en la lista.
- **Description**: Se debe de identificar el tipo genérico de activo intangible (GIA) que existen en la empresa. Para ello se debe de seleccionar de la siguiente lista:

- GIA 1: Modelo Productivo / Ejecución del Servicio
- GIA 2: Modelo Comercial o de Clientes
- GIA 3: Modelo de Oferta y Diversifiación de Servicios / Innovación
- GIA 4: Modelo de Expansión Geográfica Internacional
- GIA 5: Modelo de RRHH / Desarrollo Profesional / Principios y Valores
- GIA 6: Modelo Retributivo y de Propiedad
- GIA 7: Modelo de Marca
- GIA 8: Modelo de Relaciones Institucionales y Networking de Alto Nivel/Stakeholders 
- GIA 9: Modelo de Organización y Procesos
- GIA 10: Modelo de Estrategia de la Compañia
- GIA 11: Modelo de Gestión del Conocimiento Organizativo

## GIA
- **Type**: Integer
- **Depends on**: TIPO_GIA
- **Name**: GIA
- **Description**: Indicar el número del Tipo Genérico de Activo Intangible (GIA) seleccionado.

## Importancia del activo intangible específico para conseguir el objetiuvo de negocio
- **Type**: Integer
- **Depends on**: Objetivo_Negocio, TIPO_GIA
- **Name**: Importancia_activo_intangible
- **Description**: Se debe de asignar un valor de importancia, del 1 al 5 siendo el 1 una importancia mínima y 5 una importancia máxima, al activo intangible específico seleccionado en función de su relevancia para conseguir el objetivo de negocio fijado.

## Tipo de CI de Intellectus
- **Type**: String
- **Depends on**: TIPO_GIA, GIA
- **Name**: Tipo_de_CI_de_Intellectus
- **Validation Rule**: El `Tipo_de_CI_de_Intellectus` debe de ser uno de los valores permitidos según el `GIA` seleccionado.
- **Description**: Se debe de identificar el tipo de CI de Intellectus que corresponde al activo intangible específico seleccionado, de acuerdo al tipo genérico de activo intangible (GIA) y GIA seleccionado. Para ello se debe de seleccionar de la siguiente lista:
- GIA = 1:
    - Capital humano
    - Capital organizativo
    - Capital tecnológico
    - Capital de negocio
    - Capital social
- GIA = 2:
    - Capital humano
    - Capital organizativo
    - Capital de negocio
    - Capital social
    - Capital de emprendimiento e innovación
- GIA = 3:
    - Capital humano
    - Capital organizativo
    - Capital tecnológico
    - Capital de negocio
    - Capital de emprendimiento e innovación
- GIA = 4:
    - Capital organizativo
    - Capital de negocio
    - Capital de emprendimiento e innovación
- GIA = 5:
    - Capital humano
    - Capital organizativo
    - Capital tecnológico
    - Capital de negocio
    - Capital social
    - Capital de emprendimiento e innovación
- GIA = 6:
    - Capital humano
    - Capital organizativo
    - Capital tecnológico
    - Capital de negocio
    - Capital de emprendimiento e innovación
- GIA = 7:
    - Capital humano
    - Capital de negocio
    - Capital social
- GIA = 8:
    - Capital organizativo
    - Capital de negocio
    - Capital social
- GIA = 9:
    - Capital organizativo
    - Capital social
    - Capital de emprendimiento e innovación
- GIA = 10:
    - Capital de negocio
    - Capital social
    - Capital de emprendimiento e innovación
- GIA = 11:
    - Capital humano
    - Capital organizativo
    - Capital tecnológico
    - Capital de emprendimiento e innovación

## Identificación del Artefacto
- **Type**: String
- **Depends on**: TIPO_GIA, Objetivo_Negocio, Tipo_de_CI_de_Intellectus
- **Name**: Artefacto
- **Description**: Identificar el artefacto o producto tangible que dará soporte y materializará el activo intangible específico. Para identificar el artefacto se deben aplicar las siguientes metodologías:

### Metodología 1: Value Proposition Canvas (Osterwalder, 2014)

Aplicar el análisis siguiendo estos pasos:

1. **Customer Profile (Perfil del Cliente/Stakeholder)**:
   - **Customer Jobs**: ¿Qué tareas necesita realizar el stakeholder afectado por este activo intangible?
   - **Pains (Frustraciones)**: ¿Qué frustraciones, riesgos u obstáculos enfrenta actualmente?
   - **Gains (Beneficios)**: ¿Qué resultados o beneficios espera obtener?

2. **Value Map (Mapa de Valor)**:
   - **Products & Services**: ¿Qué artefacto (producto/servicio) puede ayudar al stakeholder?
   - **Pain Relievers**: ¿Cómo el artefacto alivia las frustraciones identificadas?
   - **Gain Creators**: ¿Cómo el artefacto genera los beneficios esperados?

3. **Fit (Encaje)**: El artefacto debe conectar directamente las necesidades del stakeholder con el activo intangible.

**Ejemplo de razonamiento**:
```
GIA 2 (Modelo Comercial) + Objetivo (Ampliar alcance a clientes) 
→ Stakeholder: Clientes potenciales online
→ Customer Job: Comprar productos sin desplazarse
→ Pain: No hay tienda física cerca
→ Gain: Comodidad y acceso 24/7
→ Artefacto: "Plataforma e-commerce con catálogo y pasarela de pago"
```

### Metodología 2: Técnicas de Innovación

Aplicar técnicas creativas para generar artefactos innovadores:

1. **SCAMPER** (Sustituir, Combinar, Adaptar, Modificar, Proponer otros usos, Eliminar, Reordenar):
   - ¿Qué soluciones existentes pueden adaptarse?
   - ¿Qué elementos pueden combinarse para crear algo nuevo?

2. **Design Thinking**:
   - Empatizar con los stakeholders
   - Definir el problema desde el activo intangible
   - Idear múltiples soluciones de artefactos
   - Seleccionar la más viable

3. **Jobs-to-be-Done**:
   - ¿Qué "trabajo" debe completar el stakeholder?
   - ¿Qué artefacto le permite completarlo mejor?

**Output esperado**: Un nombre descriptivo del artefacto que materializa el activo intangible y resuelve necesidades específicas de stakeholders.

**Validation Rule**: El artefacto debe:
- Ser concreto y accionable (un producto, sistema, proceso o servicio)
- Tener relación directa con el GIA y objetivo de negocio
- Atender necesidades de al menos un grupo de stakeholders
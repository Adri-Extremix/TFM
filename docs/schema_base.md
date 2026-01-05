# Activos Intangibles - Schema Base

## Estructura JSON Esperada

{
  "Activos_Intangibles": [
    {
      "TIPO_GIA": "string (ver catalogo_gia.md)",
      "GIA": "integer (1-11)",
      "Importancia_activo_intangible": "integer (1-5)",
      "Tipo_de_CI_de_Intellectus": "string (ver mapeo_gia_ci.md)",
      "Artefacto": "string (ver metodologia_artefactos.md)"
    }
  ]
}

## Reglas de Validación

1. `TIPO_GIA` debe estar en el catálogo GIA
2. `GIA` debe coincidir con el número del TIPO_GIA
3. `Importancia_activo_intangible` entre 1-5
4. `Tipo_de_CI_de_Intellectus` debe ser válido para el GIA seleccionado
5. El artefacto debe seguir las metodologías definidas

Para detalles, consultar documentos específicos.
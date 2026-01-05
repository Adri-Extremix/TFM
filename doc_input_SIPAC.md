# SIPAC Input Documentation

### Objetivo_Negocio

- **Type**: String
- **Description**: Describe cual es el objetivo de negocio de la empresa cliente para la que estamos haciendo el plan de DX.
- **Comments**: Debe de ser una declaración de objetivo concisa y clara, no más de 10 palabras.

### Requisito_Negocio

- **Type**: List of Strings
- **Depends on**: Objetivo_Negocio
- **Description**: Describe los requisitos de negocio que deben cumplirse para alcanzar el objetivo de negocio.
- **Comments**: Un objetivo de negocio puede tener múltiples requisitos de negocio asociados.

### Proceso

- **Type**: List of Strings
- **Depends on**: Objetivo_Negocio
- **Description**: Describe los procesos de la empresa que pueden ayudar a cumplir el objetivo de negocio.

import json
import os
import sys
import argparse

# Asegurar que podemos importar modulos locales tanto si se ejecuta desde root como desde src/
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from sipac_data import SIPAC_STEPS
except ImportError:
    print("[FATAL ERROR] No se encontró el archivo 'sipac_data.py'.")
    print("Asegúrate de que 'src/sipac_data.py' existe.")
    sys.exit(1)


class SipacWizard:
    def __init__(self, json_mode=False):
        self.data = {}
        self.steps = SIPAC_STEPS
        self.json_mode = json_mode

    def display_step_context(self, step, index, total, error_msg=None):
        """Imprime la documentación formateada para Humano/IA"""
        
        # Resolución dinámica de textos (si son funciones, se ejecutan con la data actual)
        doc_text = (
            step.documentation(self.data)
            if callable(step.documentation)
            else step.documentation
        )
        prompt_text = step.prompt(self.data) if callable(step.prompt) else step.prompt

        if self.json_mode:
            # SALIDA ESTRUCTURADA PARA EL AGENTE
            message = {
                "type": "step",
                "step_index": index,
                "total_steps": total,
                "step_key": step.key,
                "title": step.title,
                "description": doc_text.strip(),
                "examples": step.examples,
                "prompt": prompt_text,
                "current_data_summary": self.data,
                "last_error": error_msg
            }
            print(json.dumps(message, ensure_ascii=False))
            sys.stdout.flush()
        else:
            separator = "=" * 70
            print(f"\n{separator}")
            if error_msg:
                print(f" [!] ERROR PREVIO: {error_msg}")
            print(f" PASO {index + 1} de {total}: {step.title}")
            print(f"{separator}")

            print("\n<<<< CONTEXTO >>>>")
            print(doc_text.strip())

            print(f"\n<<<< EJEMPLOS >>>>")
            print(step.examples)

            print(f"\n<<<< PROMPT >>>>")
            print(f"{prompt_text}:")
            sys.stdout.flush()

    def run(self):
        if not self.json_mode:
            print("=== SIPAC: MOTOR DE GENERACIÓN DE LÓGICA DE NEGOCIO ===")
            print(f"Cargados {len(self.steps)} pasos de definición.")

        for i, step in enumerate(self.steps):
            valid_input = False
            last_error = None

            while not valid_input:
                self.display_step_context(step, i, len(self.steps), last_error)

                try:
                    # Input estándar (compatible con pipe de IA o teclado humano)
                    prompt_str = ">> " if not self.json_mode else ""
                    raw_input = input(prompt_str).strip()
                except (EOFError, KeyboardInterrupt):
                    if not self.json_mode:
                        print("\n[ABORT] Operación cancelada por el usuario.")
                    sys.exit(1)

                # 1. Validación Lógica (definida en sipac_data.py)
                try:
                    if step.validator:
                        # Intentar pasar data al validador para validaciones contextuales
                        try:
                            is_valid = step.validator(raw_input, self.data)
                        except TypeError:
                            # Fallback para validadores simples que solo aceptan x
                            is_valid = step.validator(raw_input)

                        if not is_valid:
                            msg = f"Entrada inválida: '{raw_input}'"
                            if not self.json_mode:
                                print(f"\n[ERROR] {msg}")
                                print(
                                    "Por favor, revisa los EJEMPLOS y la DOCUMENTACIÓN e inténtalo de nuevo."
                                )
                            last_error = msg
                            continue

                    # 2. Conversión de Tipo
                    final_value = step.cast_func(raw_input)
                    self.data[step.key] = final_value
                    valid_input = True
                    last_error = None

                    if not self.json_mode:
                        print(f"[OK] Valor registrado: {final_value}")

                except Exception as e:
                    msg = f"Fallo al procesar el dato: {e}"
                    if not self.json_mode:
                        print(f"\n[ERROR SISTEMA] {msg}")
                    last_error = msg

        self.finalize()

    def finalize(self):
        results = self.calculate_results(self.data)

        if self.json_mode:
            print(json.dumps({"type": "result", "data": results}, indent=2, ensure_ascii=False))
        else:
            print("\n" + "=" * 70)
            print(" RECOLECCIÓN COMPLETADA - GENERANDO RESULTADOS")
            print("=" * 70)

            print("\n--- RESULTADOS CALCULADOS ---")
            print(json.dumps(results, indent=2, ensure_ascii=False))

    def calculate_results(self, data):
        """
        Simula las fórmulas que tenías en el Excel.
        """
        output = {"inputs": data, "analisis": {}}

        # Ejemplo de lógica de negocio basada en inputs
        # 1. Cálculo de Amortización
        if data.get("tipo_activo") == "HW":
            amort_years = 5
        elif data.get("tipo_activo") == "SW":
            amort_years = 3
        else:
            amort_years = 0  # SRV es gasto corriente

        output["analisis"]["amortizacion_anos"] = amort_years

        # 2. Cálculo de Coste de Mantenimiento Anual
        # Base: 10% del CAPEX. Multiplicador por criticidad (1.0, 1.15, 1.30)
        if "presupuesto_base" in data and "criticidad" in data:
            base_maint = data["presupuesto_base"] * 0.10
            crit_factor = (
                1 + (data["criticidad"] - 1) * 0.15
            )  # 1->1.0, 2->1.15, 3->1.30

            output["analisis"]["coste_mantenimiento_anual"] = round(
                base_maint * crit_factor, 2
            )

        return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SIPAC: Sistema Interactivo de Procesos")
    parser.add_argument("--json", action="store_true", help="Habilitar salida JSON estructurada para agentes de IA")
    args = parser.parse_args()

    wizard = SipacWizard(json_mode=args.json)
    wizard.run()
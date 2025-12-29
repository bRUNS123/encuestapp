
import os
import sys
import subprocess
import time

# Script para reiniciar todas las preguntas automáticamente desde questions.json
# Ejecuta backend/reset_and_load_data.py enviando "SI" automáticamente

print("\n🚀 INICIANDO REINICIO COMPLETO DE PREGUNTAS (JSON)\n")

print("▶️  Ejecutando cargador de datos...")
try:
    # Ejecutamos el script y le pasamos "SI\n" al input
    process = subprocess.Popen(
        [sys.executable, "backend/reset_and_load_data.py"],
        stdin=subprocess.PIPE,
        stdout=sys.stdout, # Mostrar salida en tiempo real
        stderr=sys.stderr,
        text=True
    )
    
    # Enviar confirmación automática
    process.communicate(input="SI\n")
    
    if process.returncode == 0:
        print("\n✅ ¡REINICIO COMPLETADO EXITOSAMENTE!")
    else:
        print("\n❌ Error al recargar base de datos")

except Exception as e:
    print(f"   ❌ Error ejecutando script de carga: {e}")
    sys.exit(1)

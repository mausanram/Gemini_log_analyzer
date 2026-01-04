
# 🤖 Analizador de Logs con Gemini (GenAI)

Este proyecto implementa un pipeline automatizado para la clasificación y análisis de logs de servidor utilizando Modelos de Lenguaje Grande (LLMs), específicamente **Google Gemini 2.5 Flash**. El sistema procesa archivos de logs crudos (`.txt`), aplica ingeniería de prompts para extraer el contexto semántico y genera una salida estructurada (`.json`) lista para ser consumida por dashboards o sistemas de monitoreo.

## ¿Qué hace el script?
Este script es un analizador automatizado de logs que utiliza un Modelo de Lenguaje Grande (LLM) 
de Google para clasificar registros. Especificamente utiliza los modelos Gemini 2.5 Flash (o 2.0 Flash,
recomendado para hacer pruebas). El script realiza los siguientes pasos:
1. Lee la GEMINI_API_KEY de un archivo .env para no exponer credenciales sensibles.
2. Abre el archivo logs.txt y lee cada línea como un registro de log individual, ignorando líneas vacías.
3. Itera sobre cada uno de los logs que se identificaron y contacta a la API de 
   Google Gemini (modelo 2.5 Flash o 2.0 Flash).
4. Envía un prompt específico al modelo, pidiéndole que actúe como un analista experto y devuelva etiquetas 
   temáticas (ej. ["SQL-query", "timeout-error"]) en un formato JSON estricto.
5. Implementa una pausa estratégica (time.sleep()) entre cada llamada para evitar que la API se sature (ver
   las "Decisiones Técnicas Relevantes" para mas detalles de esta parte). 
6. Al finalizar el análisis, el script recopila todos los resultados y los guarda en un archivo output.json, 
   formateado con el log_id, el texto original y las etiquetas generadas por la IA.

## Requisitos Previos 
* Versión de Python: Python 3.10.12 o superior.
* API Key de Google AI Studio: Se requiere una API Key para poder ejecutar el script. Puedes generar 
  una en: **[Google AI Studio](https://aistudio.google.com/app/apikey)**.

### Pasos de Ejecución
1.  Clonar el repositorio y crear un entorno virtual y activarlo: 
   ```bash
   python -m venv venv
   ```

2. Activa el ambiente virtual (para Linux/macOs):      
   ```bash 
   source venv/bin/activate
   ```
*(En Windows: `.\venv\Scripts\Activate.ps1`)*

3.  Instalar las dependencias: 
   ```bash
   pip install -r requirements.txt
   ```

4.  Configura las credenciales: crear un archivo '.env' en la raíz del proyecto y añade la llave: 
   ```ini 
   GEMINI_API_KEY="TU_API_KEY_AQUI"
   ```

5.  Ejecutar el script:
   ```bash 
   python main.py
   ``` 

### Ejemplo de Funcionamiento
Se reciben bloques logs en formato .txt como el que se muestra a continuación:
```text
[2025-10-20 09:13:42] [INFO] Agent DBConnector initialized. Awaiting query request.
[2025-10-20 09:13:45] [USER INPUT] "Muéstrame los cursos disponibles de Power BI con certificación."
[2025-10-20 09:13:45] [DEBUG] Building SQL query...
[2025-10-20 09:13:46] [SQL] SELECT nombre, certificacion, disponible FROM cursos WHERE tecnologia_id = 'Power BI';
[2025-10-20 09:13:47] [INFO] Query executed successfully. 12 records retrieved.
[2025-10-20 09:13:48] [LLM RESPONSE] “Encontré 12 cursos disponibles con certificación Power BI.”
```
Posteriormente el script procesa cada línea, consulta a la API de Gemini y genera una estructura JSON estandarizada donde
se calsifica cada uno de los bloques logs con máximo 3 etiquetas estandarizadas, como el que se muestra abajo:
```JSON
[
  {
    "log_id": 1,
    "timestamp": "2023-11-05 08:30:15",
    "tags": ["performance-issue", "sql-query", "high-latency"],
    "analysis": "Query executing smoothly but exceeding latency threshold."
  }
]
```



### Decisiones Técnicas
**Elección del modelo:**
  Se eligió el modelo gemini-2.5-flash a pesar de que el gemini-2.0-flash ofrece un límite de peticiones por 
  minuto (RPM) superior (10 RPM y 15 RPM, respectivamente). La razon es que para una tarea de clasificación de logs, 
  la calidad y precisión de las etiquetas es el objetivo principal y debido a que el modelo 2.5 Flash es de una 
  generación más reciente y cuenta con capacidades de razonamiento superiores, proporciona una clasificación más 
  inteligente y útil de los logs. En este proyecto se priorizó obtener un resultado de mayor calidad sobre una 
  ejecución marginalmente más rápida. 

**Manejo de RPM:** 
  La API gratuita de Gemini impone límites estrictos de frecuencia que deben ser manejados para
  evitar fallos. Para el modelo 2.5 Flash el nivel gratuito tiene un límite de 10 peticiones por minuto (RPM), 
  por lo que un bucle simple fallaría con un error 429 (Too Many Requests) después del décimo log. 
  Para garantizar que el script procese logs de forma 100% robusta, se implementó un time.sleep(6.1) fijo 
  entre cada llamada a la API. Este delay asegura una tasa de ~9.8 peticiones por minuto, operando de forma 
  segura dentro del límite. Esta estrategia garantiza que el script funcione correctamente en cualquier máquina, 
  independientemente de la velocidad de su red o de la latencia variable de los servidores de Google.  

   **Nota:** el delay que se requiere para el modelo 2.0 Flash con un RPM de 15 es de 4.1 seg. Tomando en cuenta
   que el límite de peticiones por día (RPD) para 2.5 Flash es de 250 y para 2.0 Flash es de 200, la diferencia 
   de tiempos al analizar 200 logs es de alrededor de 7 minutos, lo cual no es un tiempo enorme a estas escalas. 
   Esto es una razon mas para utilizar 2.5 Flash al final.

**Gestión Segura de Credenciales (python-dotenv):**
  Para evitar exponer credenciales sensibles (la API Key) directamente en el código fuente, se utiliza la 
  librería "python-dotenv" para cargar la GEMINI_API_KEY desde un archivo local ".env". Este archivo .env se 
  excluye del control de versiones (a través de .gitignore), asegurando que la clave secreta nunca se 
  comparta públicamente en repositorios como GitHub. 

**Propmt utilizado:**
   El propt que se manda al modelo fue optimizado para que las respuestas obtenidas fueran mas precisas, es por 
   eso que en el mismo propt se pide que las etiquetas las realice en lenguaje ingles (ya que el ejemplo que se
   proporciona está en este idioma), además ya que se pide como máximo 3 etiquetas esto genera que el modelo deba
   pensar y razonar cuales son las mejores opciones, y no simplemente tomar palabras que vienen dentro del propio
   texto. Tambien se solicita al modelo que estandarice sus respuestas para que no existan muchas etiquetas diferentes
   para una misma característica que compartan los bloques de logs. Con todo esto se reduce el riesgo de que el modelo
   pueda cometer errores como alucionaciones.

---
## 👤 Autor

**Mauricio Sánchez**
* [LinkedIn](https://www.linkedin.com/in/mauricio-s%C3%A1nchez-ram%C3%ADrez-497a92285)
* [GitHub](https://github.com/mausanram)

*Este proyecto fue desarrollado como parte de un portafolio de Ingeniería de Datos e IA.*


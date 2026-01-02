import google.generativeai as genai
from flask import Flask, request, jsonify
import os
# 1. CONFIGURACIÓN DE LA IA (GEMINI 2.5 FLASH)
# Coloca aquí tu API Key de Google AI Studio
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Configuración del modelo para respuestas precisas y cortas
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_output_tokens": 100, # Alexa corta respuestas muy largas
}

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    generation_config=generation_config
)

app = Flask(__name__)

# 2. FUNCIONES AUXILIARES
def consultar_ia(pregunta):
    try:
        # Instrucción de sistema para control de voz
        prompt = f"Eres un asistente de voz. Responde de forma natural y directa en menos de 2 sentencias: {pregunta}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Tuve un problema al procesar la información."
    

def build_response(texto_voz, terminar_sesion=False):
    """Crea el JSON que Alexa entiende"""
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": texto_voz
            },
            "shouldEndSession": terminar_sesion
        }
    }

# 3. RUTA PRINCIPAL (ENDPOINT)
@app.route("/", methods=['POST'])
def alexa_interface():
    data = request.json
    request_type = data['request']['type']
    
    print(f"\n--- Nueva petición: {request_type} ---")

    # Cuando dices: "Alexa, abre asistente virtual"
    if request_type == "LaunchRequest":
        return jsonify(build_response("Sistemas de Inteligencia Artificial 2.5 activos. ¿Qué deseas consultar?"))

    # Cuando haces una pregunta (PreguntaIntent)
    elif request_type == "IntentRequest":
        intent_name = data['request']['intent']['name']
        print(f"DEBUG: El intent recibido es: {intent_name}") # Esto te dirá el nombre real
        
        if intent_name == "preguntaIntent":
            try:
                # Extraemos lo que el usuario dijo del slot 'tupregunta'
                pregunta_usuario = data['request']['intent']['slots']['tupregunta']['value']
                print(f"Usuario preguntó: {pregunta_usuario}")
                
                # Consultamos a Gemini
                respuesta_ia = consultar_ia(pregunta_usuario)
                print(f"IA respondió: {respuesta_ia}")
                
                return jsonify(build_response(respuesta_ia))
            except KeyError:
                return jsonify(build_response("Te escuché, pero no pude procesar la pregunta. Intenta decir: dime, y luego tu pregunta."))

    # Cuando el usuario dice "detener" o "cancelar"
    elif request_type == "SessionEndedRequest":
        return jsonify(build_response("Cerrando conexión. Hasta pronto.", True))

    return jsonify(build_response("Estoy escuchando."))

if __name__ == "__main__":
    print("Iniciando servidor en puerto 5000...")

    app.run(port=5000, debug=True)

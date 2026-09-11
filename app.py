import json
import random
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "clave_secreta_italiano_app"

def cargar_preguntas():
    with open('preguntas.json', 'r', encoding='utf-8') as file:
        return json.load(file)

@app.route('/')
def inicio():
    session['correctas'] = 0
    session['incorrectas'] = 0
    session['respondidas'] = []
    
    preguntas = cargar_preguntas()
    niveles = sorted(list(set(p['nivel'] for p in preguntas)))
    temas = sorted(list(set(p['tema'] for p in preguntas)))
    
    return render_template('inicio.html', niveles=niveles, temas=temas)

@app.route('/iniciar_quiz', methods=['POST'])
def iniciar_quiz():
    session['nivel'] = request.form.get('nivel')
    session['tema'] = request.form.get('tema')
    session['correctas'] = 0
    session['incorrectas'] = 0
    session['respondidas'] = []
    return redirect(url_for('ver_pregunta'))

@app.route('/pregunta')
def ver_pregunta():
    preguntas = cargar_preguntas()
    nivel_sel = session.get('nivel')
    tema_sel = session.get('tema')
    respondidas_ids = session.get('respondidas', [])

    filtradas = [
        p for p in preguntas 
        if (not nivel_sel or p['nivel'] == nivel_sel) and (not tema_sel or p['tema'] == tema_sel)
    ]

    pendientes = [p for p in filtradas if p['id'] not in respondidas_ids]

    if not pendientes:
        if not filtradas:
            return "No hay preguntas disponibles con los filtros seleccionados. <a href='/'>Volver al inicio</a>"
        
        return render_template(
            'final.html', 
            correctas=session.get('correctas', 0), 
            incorrectas=session.get('incorrectas', 0),
            total=len(filtradas)
        )

    pregunta_actual = random.choice(pendientes)
    
    # Mezclar según el tipo de pregunta si corresponde
    if 'opciones_imagen' in pregunta_actual:
        opciones_mezcladas = pregunta_actual['opciones_imagen'].copy()
        random.shuffle(opciones_mezcladas)
        pregunta_actual['opciones_imagen'] = opciones_mezcladas
    elif 'opciones' in pregunta_actual:
        opciones_mezcladas = pregunta_actual['opciones'].copy()
        random.shuffle(opciones_mezcladas)
        pregunta_actual['opciones'] = opciones_mezcladas
    # Si es de tipo 'texto', no requiere mezclar opciones

    return render_template(
        'pregunta.html', 
        pregunta=pregunta_actual,
        correctas=session.get('correctas', 0),
        incorrectas=session.get('incorrectas', 0)
    )

@app.route('/responder', methods=['POST'])
def responder():
    pregunta_id = int(request.form.get('pregunta_id'))
    # .strip() elimina espacios accidentales al inicio o final
    opcion_elegida = request.form.get('opcion', '').strip()

    preguntas = cargar_preguntas()
    pregunta = next((p for p in preguntas if p['id'] == pregunta_id), None)

    # Comparación tolerante a mayúsculas/minúsculas
    respuesta_usuario = opcion_elegida.lower()
    respuesta_correcta = pregunta['correcta'].strip().lower()

    es_correcta = (respuesta_usuario == respuesta_correcta)

    if es_correcta:
        session['correctas'] = session.get('correctas', 0) + 1
    else:
        session['incorrectas'] = session.get('incorrectas', 0) + 1

    respondidas = session.get('respondidas', [])
    if pregunta_id not in respondidas:
        respondidas.append(pregunta_id)
        session['respondidas'] = respondidas

    return render_template(
        'resultado.html', 
        pregunta=pregunta, 
        opcion_elegida=opcion_elegida, 
        es_correcta=es_correcta,
        correctas=session.get('correctas', 0),
        incorrectas=session.get('incorrectas', 0)
    )

if __name__ == '__main__':
    app.run(debug=True)
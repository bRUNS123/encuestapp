#!/usr/bin/env python
"""
Script para limpiar datos y cargar nuevas preguntas desde questions.json
- Borra todas las preguntas existentes
- Borra todos los votos (Answer)  
- Mantiene usuarios (email y password)
- Carga preguntas nuevas con sus tipos correspondientes
"""
import os
import django
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from questions.models import Question, QuestionOption
from answers.models import Answer
from categories.models import Category
import json
from datetime import datetime, timedelta

# Path to questions.json
json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'questions.json')

with open(json_path, 'r', encoding='utf-8') as f:
    category_questions = json.load(f)

def clean_database():
    """Limpia preguntas y votos, mantiene usuarios"""
    print("🗑️  Limpiando base de datos...")
    
    # Borrar todos los votos
    answer_count = Answer.objects.count()
    Answer.objects.all().delete()
    print(f"   ✅ Eliminados {answer_count} votos")
    
    # Borrar todas las opciones de preguntas
    option_count = QuestionOption.objects.count()
    QuestionOption.objects.all().delete()
    print(f"   ✅ Eliminadas {option_count} opciones")
    
    # Borrar todas las preguntas
    question_count = Question.objects.count()
    Question.objects.all().delete()
    print(f"   ✅ Eliminadas {question_count} preguntas")
    
    print("\n✨ Base de datos limpiada (usuarios mantenidos)\n")


def determine_question_type(options):
    """
    Determina el tipo de pregunta basado en las opciones
    """
    if len(options) == 2:
        # Si son exactamente 2 opciones
        options_lower = [str(opt).lower() for opt in options]
        if set(options_lower) == {'si', 'no'}:
            return 'binary'
        else:
            return 'dropdown'
    
    elif len(options) == 5:
        # Si son 5 opciones y todas son números 1-5
        try:
            nums = [int(opt) for opt in options]
            if nums == [1, 2, 3, 4, 5]:
                return 'scale'
            else:
                return 'dropdown'
        except:
            return 'dropdown'
    
    else:
        # Cualquier otro caso es dropdown
        return 'dropdown'


def load_new_questions():
    """Carga las preguntas desde questions.json (Nueva Estructura)"""
    print("📝 Cargando nuevas preguntas desde JSON...\n")
    
    total_created = 0
    
    # Check for 'sections' key in new format
    if 'sections' in category_questions:
        sections = category_questions['sections']
    else:
        # Fallback for old format (dictionary of lists)
        print("⚠️ Formato antiguo detectado, adaptando...")
        sections = []
        for key, val in category_questions.items():
            sections.append({'id': key.lower(), 'title': key, 'questions': val})

    for section in sections:
        section_id = section.get('id', '').lower()
        if section_id != 'personal':
            print(f"Skipping section: {section_id}")
            continue

        category_name = section.get('id').upper() # Use ID as category name (e.g. PERSONAL)
        questions = section.get('questions', [])
        
        # Obtener o crear la categoría
        # Map user-friendly title to description if needed
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={'description': section.get('title', category_name)}
        )
        
        print(f"📁 {category_name} - {len(questions)} preguntas")
        
        for q_data in questions:
            # Determinar tipo de pregunta (priorizar el definido en el JSON)
            if 'question_type' in q_data:
                q_type = q_data['question_type']
            else:
                q_type = determine_question_type(q_data.get('options', []))
            
            # Use 'description' from JSON as subtitle/help_text if available? 
            # Model doesn't have description field, skipping for now.
            
            # Crear la pregunta
            question = Question.objects.create(
                title=q_data['title'],
                category=category,
                question_type=q_type,
                creation_date=datetime.now(),
                expiration_date=datetime.now() + timedelta(days=30),
                cantidad_votos=0
            )
            
            # Crear las opciones
            if 'options' in q_data:
                for option_text in q_data['options']:
                    QuestionOption.objects.create(
                        question=question,
                        title=str(option_text),
                        votes=0
                    )
            
            total_created += 1
            
            # Ícono según tipo
            type_icons = {
                'binary': '✓',
                'scale': '⭐',
                'dropdown': '📋',
                'date': '📅',
                'slider': '📏'
            }
            icon = type_icons.get(q_type, '❓')
            
            print(f"   {icon} [{q_type}] {question.title[:60]}...")
    
    print(f"\n✅ Total: {total_created} preguntas creadas (Solo PERSONAL)\n")


def show_summary():
    """Muestra un resumen de la base de datos"""
    print("=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    from profiles.models import Profile
    
    print(f"👥 Usuarios: {Profile.objects.count()}")
    print(f"📋 Preguntas: {Question.objects.count()}")
    print(f"   - Binarias (Sí/No): {Question.objects.filter(question_type='binary').count()}")
    print(f"   - Escala (1-5): {Question.objects.filter(question_type='scale').count()}")
    print(f"   - Dropdown: {Question.objects.filter(question_type='dropdown').count()}")
    print(f"✓ Opciones: {QuestionOption.objects.count()}")
    print(f"🗳️  Votos: {Answer.objects.count()}")
    
    print("\n📁 Por categoría:")
    for category in Category.objects.all():
        count = Question.objects.filter(category=category).count()
        if count > 0:
            print(f"   - {category.name}: {count} preguntas")
    
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔄 REESTRUCTURACIÓN DE BASE DE DATOS - DECIDELIBRE")
    print("="*60 + "\n")
    
    # Confirmación
    confirm = input("⚠️  Esto borrará TODAS las preguntas y votos.\n¿Continuar? (escribe 'SI' para confirmar): ")
    
    if confirm.upper() != 'SI':
        print("\n❌ Operación cancelada\n")
        sys.exit(0)
    
    print("\n🚀 Iniciando proceso...\n")
    
    try:
        # 1. Limpiar
        clean_database()
        
        # 2. Cargar nuevas preguntas
        load_new_questions()
        
        # 3. Mostrar resumen
        show_summary()
        
        print("\n✅ ¡Proceso completado exitosamente!\n")
        
    except Exception as e:
        print(f"\n❌ Error durante el proceso: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

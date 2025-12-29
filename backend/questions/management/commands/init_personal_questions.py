import os
import re
from django.core.management.base import BaseCommand
from categories.models import Category
from questions.models import Question, QuestionOption

class Command(BaseCommand):
    help = 'Initializes PERSONAL category questions, including nationalities from SQL file'

    def handle(self, *args, **options):
        self.stdout.write("Initializing PERSONAL questions...")

        # 1. Create/Get Category
        category, created = Category.objects.get_or_create(
            name='PERSONAL',
            defaults={'description': 'Información personal del usuario'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Category 'PERSONAL' created"))
        else:
            self.stdout.write("Category 'PERSONAL' exists")

        # 2. Define Standard Questions (Dropdowns and Open Text)
        PERSONAL_QUESTIONS = [
            {
                'title': 'Estado Civil',
                'type': 'dropdown',
                'options': ['Soltero/a', 'Casado/a', 'Viudo/a', 'Divorciado/a', 'Conviviente Civil', 'Separado/a']
            },
            {
                'title': 'Nivel Educacional',
                'type': 'dropdown',
                'options': ['Básica Incompleta', 'Básica Completa', 'Media Incompleta', 'Media Completa', 'Técnico Superior', 'Universitario', 'Postgrado (Magíster/Doctorado)']
            },
            {
                'title': 'Situación Laboral', # Was "Employment Status"
                'type': 'dropdown',
                'options': ['Trabajador Dependiente', 'Trabajador Independiente', 'Desempleado', 'Estudiante', 'Jubilado/Pensionado', 'Dueña/o de Casa']
            },
            {
                'title': 'Profesión / Oficio',
                'type': 'open',
                'options': [] # No options for open text
            },
            {
                'title': 'Religión / Creencia',
                'type': 'dropdown',
                'options': ['Católica', 'Evangélica/Protestante', 'Ateo/Agnóstico', 'Judía', 'Musulmana', 'Budista', 'Espiritual sin religión', 'Otra']
            },
            {
                'title': 'Tendencia Política',
                'type': 'dropdown',
                'options': ['Izquierda', 'Centro Izquierda', 'Centro', 'Centro Derecha', 'Derecha', 'Independiente', 'Libertario', 'Ninguna']
            },
            {
                'title': 'Tipo de Vivienda',
                'type': 'dropdown',
                'options': ['Casa Propia', 'Casa Arrendada', 'Departamento Propio', 'Departamento Arrendado', 'Allegado/Familiar', 'Otro']
            },
            {
                'title': 'Previsión de Salud',
                'type': 'dropdown',
                'options': ['Fonasa A', 'Fonasa B', 'Fonasa C', 'Fonasa D', 'Isapre', 'Capredena / Dipreca', 'Ninguna / Particular']
            }
        ]

        # 3. Create Standard Questions
        for q_data in PERSONAL_QUESTIONS:
            question, q_created = Question.objects.get_or_create(
                title=q_data['title'],
                category=category,
                defaults={'question_type': q_data['type']}
            )
            
            if q_created:
                self.stdout.write(f"Created question: {q_data['title']}")
            
            # Create Options for this question if it's dropdown
            if q_data['type'] == 'dropdown' and q_data['options']:
                for opt_text in q_data['options']:
                    QuestionOption.objects.get_or_create(question=question, title=opt_text)

        # 4. Handle Nacionalidad (From JSON)
        json_path = r'd:\PROGRAMACION\decidelibre-gravity\nacionalidades.json'
        
        if os.path.exists(json_path):
            self.stdout.write("Processing Nacionalidades from JSON...")
            
            import json
            
            nat_question, nat_created = Question.objects.get_or_create(
                title='Nacionalidad',
                category=category,
                defaults={'question_type': 'dropdown'}
            )

            # Read JSON file
            with open(json_path, 'r', encoding='utf-8') as f:
                countries = json.load(f)

            if countries:
                self.stdout.write(f"Found {len(countries)} nationalities in JSON.")
                count = 0
                for country_name in countries:
                    obj, created = QuestionOption.objects.get_or_create(
                        question=nat_question,
                        title=country_name
                    )
                    if created:
                        count += 1
                self.stdout.write(self.style.SUCCESS(f"Processed {len(countries)} nationalities. Created {count} new options."))
            else:
                self.stdout.write(self.style.WARNING("No nationalities found in JSON file."))

        else:
             self.stdout.write(self.style.ERROR(f"JSON file not found at {json_path}"))

        self.stdout.write(self.style.SUCCESS("Personal questions initialization finished."))

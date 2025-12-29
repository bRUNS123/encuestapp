from django.core.management.base import BaseCommand
from categories.models import Category
from questions.models import Question, QuestionOption

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        category_questions = {
            "salud": [
                {"title": "Haces ejercicio regularmente?", "options": ["Si", "No"]},
                {"title": "Sigues una dieta balanceada?", "options": ["Si", "No"]},
                {"title": "Te haces chequeos medicos anuales?", "options": ["Si", "No"]},
                {"title": "Tienes un medico de cabecera?", "options": ["Si", "No"]},
                {"title": "Te vacunas segun el calendario?", "options": ["Si", "No"]},
                {"title": "Consumes suficientes frutas y verduras?", "options": ["Si", "No"]},
                {"title": "Bebes al menos dos litros de agua al dia?", "options": ["Si", "No"]},
                {"title": "Duermes al menos 8 horas por noche?", "options": ["Si", "No"]},
                {"title": "Evitas el consumo excesivo de alcohol?", "options": ["Si", "No"]},
                {"title": "Te sientes generalmente saludable?", "options": ["Si", "No"]}
            ],
            "deporte": [
                {"title": "Practicas algun deporte regularmente?", "options": ["Si", "No"]},
                {"title": "Te gusta ver deportes en la television?", "options": ["Si", "No"]},
                {"title": "Participas en competencias deportivas?", "options": ["Si", "No"]},
                {"title": "Prefieres deportes individuales o en equipo?", "options": ["Individuales", "Equipo"]},
                {"title": "Eres aficionado de algun equipo deportivo?", "options": ["Si", "No"]},
                {"title": "Te gusta asistir a eventos deportivos?", "options": ["Si", "No"]},
                {"title": "Sigues las noticias deportivas?", "options": ["Si", "No"]},
                {"title": "Practicas deportes al aire libre?", "options": ["Si", "No"]},
                {"title": "Te interesa el rendimiento deportivo?", "options": ["Si", "No"]},
                {"title": "Has tomado alguna clase de deporte?", "options": ["Si", "No"]}
            ],
            "tecnologia": [
                {"title": "Te gusta estar al dia con las nuevas tecnologias?", "options": ["Si", "No"]},
                {"title": "Usas dispositivos inteligentes?", "options": ["Si", "No"]},
                {"title": "Sigues blogs o noticias de tecnologia?", "options": ["Si", "No"]},
                {"title": "Te interesa la programacion?", "options": ["Si", "No"]},
                {"title": "Participas en foros de tecnologia?", "options": ["Si", "No"]},
                {"title": "Prefieres Android o iOS?", "options": ["Android", "iOS"]},
                {"title": "Te interesan las innovaciones tecnologicas?", "options": ["Si", "No"]},
                {"title": "Usas redes sociales regularmente?", "options": ["Si", "No"]},
                {"title": "Has asistido a eventos de tecnologia?", "options": ["Si", "No"]},
                {"title": "Te gustan los videojuegos?", "options": ["Si", "No"]}
            ],
            "entretenimiento": [
                {"title": "Vas al cine con frecuencia?", "options": ["Si", "No"]},
                {"title": "Prefieres series o peliculas?", "options": ["Series", "Peliculas"]},
                {"title": "Te gusta la musica en vivo?", "options": ["Si", "No"]},
                {"title": "Participas en actividades artisticas?", "options": ["Si", "No"]},
                {"title": "Lees libros de ficcion?", "options": ["Si", "No"]},
                {"title": "Te gusta el teatro?", "options": ["Si", "No"]},
                {"title": "Sigues a youtubers o streamers?", "options": ["Si", "No"]},
                {"title": "Participas en juegos de mesa?", "options": ["Si", "No"]},
                {"title": "Te gustan los parques tematicos?", "options": ["Si", "No"]},
                {"title": "Asistes a conciertos?", "options": ["Si", "No"]}
            ],
            "politica": [
                {"title": "Te interesa la politica local?", "options": ["Si", "No"]},
                {"title": "Participas en debates politicos?", "options": ["Si", "No"]},
                {"title": "Sigues las noticias politicas?", "options": ["Si", "No"]},
                {"title": "Tienes una afiliacion politica?", "options": ["Si", "No"]},
                {"title": "Te importa el activismo politico?", "options": ["Si", "No"]},
                {"title": "Participas en manifestaciones politicas?", "options": ["Si", "No"]},
                {"title": "Te interesa la politica internacional?", "options": ["Si", "No"]},
                {"title": "Lees libros sobre politica?", "options": ["Si", "No"]},
                {"title": "Debates sobre politica en redes sociales?", "options": ["Si", "No"]},
                {"title": "Eres miembro de algun partido politico?", "options": ["Si", "No"]}
            ],
            "sociedad": [
                {"title": "Te gusta salir con amigos?", "options": ["Si", "No"]},
                {"title": "Participas en eventos comunitarios?", "options": ["Si", "No"]},
                {"title": "Te gusta conocer gente nueva?", "options": ["Si", "No"]},
                {"title": "Organizas reuniones sociales?", "options": ["Si", "No"]},
                {"title": "Usas aplicaciones de citas?", "options": ["Si", "No"]},
                {"title": "Prefieres actividades sociales o solitarias?", "options": ["Sociales", "Solitarias"]},
                {"title": "Te gusta participar en redes sociales?", "options": ["Si", "No"]},
                {"title": "Asistes a eventos culturales?", "options": ["Si", "No"]},
                {"title": "Te consideras una persona extrovertida?", "options": ["Si", "No"]},
                {"title": "Te gusta ayudar en eventos beneficos?", "options": ["Si", "No"]}
            ],
            "mundial": [
                {"title": "Te interesan las noticias internacionales?", "options": ["Si", "No"]},
                {"title": "Sigues la economia global?", "options": ["Si", "No"]},
                {"title": "Te preocupa el cambio climatico?", "options": ["Si", "No"]},
                {"title": "Te interesa la politica internacional?", "options": ["Si", "No"]},
                {"title": "Lees sobre culturas extranjeras?", "options": ["Si", "No"]},
                {"title": "Te gustan los eventos deportivos internacionales?", "options": ["Si", "No"]},
                {"title": "Participas en debates sobre problemas globales?", "options": ["Si", "No"]},
                {"title": "Has viajado al extranjero?", "options": ["Si", "No"]},
                {"title": "Te interesa aprender idiomas extranjeros?", "options": ["Si", "No"]},
                {"title": "Sigues las tendencias globales en redes sociales?", "options": ["Si", "No"]}
            ],
            "educacion": [
                {"title": "Te gusta aprender cosas nuevas?", "options": ["Si", "No"]},
                {"title": "Te interesa la educacion online?", "options": ["Si", "No"]},
                {"title": "Sigues algun curso extracurricular?", "options": ["Si", "No"]},
                {"title": "Lees libros educativos?", "options": ["Si", "No"]},
                {"title": "Te gustan los documentales educativos?", "options": ["Si", "No"]},
                {"title": "Asistes a conferencias o seminarios?", "options": ["Si", "No"]},
                {"title": "Participas en talleres educativos?", "options": ["Si", "No"]},
                {"title": "Te interesa la investigacion academica?", "options": ["Si", "No"]},
                {"title": "Tomas notas durante las clases?", "options": ["Si", "No"]},
                {"title": "Eres miembro de algun club academico?", "options": ["Si", "No"]}
            ]
        }

        self.stdout.write('Deleting existing data...')
        # Note: Deleting categories will cascade delete questions and options
        Category.objects.all().delete()
        
        for category_name, questions in category_questions.items():
            category = Category.objects.create(name=category_name)
            self.stdout.write(f'Created category: {category_name}')
            
            for q_data in questions:
                question = Question.objects.create(
                    title=q_data['title'],
                    category=category
                )
                
                for opt_text in q_data['options']:
                    QuestionOption.objects.create(
                        question=question,
                        title=opt_text
                    )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))

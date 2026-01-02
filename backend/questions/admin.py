from django.contrib import admin
from .models import Question, QuestionOption, QuestionRating


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1
    fields = ('title', 'votes')
    readonly_fields = ('votes',)
    verbose_name = "Opción de respuesta"
    verbose_name_plural = "Opciones de respuesta"


class QuestionRatingInline(admin.TabularInline):
    model = QuestionRating
    extra = 0
    can_delete = False
    fields = ('user', 'score', 'created_at')
    readonly_fields = ('user', 'score', 'created_at')
    verbose_name = "Calificación"
    verbose_name_plural = "Calificaciones"
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'question_type', 'cantidad_votos', 'rating_average', 'owner', 'creation_date')
    list_filter = ('question_type', 'category', 'creation_date')
    search_fields = ('title', 'category__name', 'owner__email')
    readonly_fields = ('creation_date', 'cantidad_votos', 'rating_average', 'rating_count')
    
    fieldsets = (
        ('Información básica', {
            'fields': ('title', 'question_type', 'category', 'owner')
        }),
        ('Fechas', {
            'fields': ('creation_date', 'expiration_date'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('cantidad_votos', 'rating_average', 'rating_count'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QuestionOptionInline, QuestionRatingInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category', 'owner')


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'question', 'votes')
    list_filter = ('question__category',)
    search_fields = ('title', 'question__title')
    readonly_fields = ('votes',)


@admin.register(QuestionRating)
class QuestionRatingAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('question__title', 'user__email')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False

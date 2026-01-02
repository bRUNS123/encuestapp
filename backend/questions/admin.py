from django.contrib import admin
from django.db import models as django_models
from .models import Question, QuestionOption, QuestionRating, QuestionReport


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




class QuestionReportInline(admin.TabularInline):
    model = QuestionReport
    extra = 0
    can_delete = True
    fields = ('reporter', 'reason', 'description', 'created_at', 'reviewed')
    readonly_fields = ('reporter', 'created_at')
    verbose_name = "Reporte"
    verbose_name_plural = "Reportes"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'question_type', 'cantidad_votos', 'rating_average', 'owner', 'creation_date', 'report_count')
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
    
    inlines = [QuestionOptionInline, QuestionRatingInline, QuestionReportInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category', 'owner').annotate(
            reports_count=django_models.Count('reports')
        )
    
    def report_count(self, obj):
        return obj.reports_count if hasattr(obj, 'reports_count') else obj.reports.count()
    report_count.short_description = 'Reportes'
    report_count.admin_order_field = 'reports_count'


@admin.register(QuestionReport)
class QuestionReportAdmin(admin.ModelAdmin):
    list_display = ('question', 'reporter', 'reason', 'created_at', 'reviewed')
    list_filter = ('reason', 'reviewed', 'created_at')
    search_fields = ('question__title', 'reporter__email', 'description')
    readonly_fields = ('created_at',)
    list_editable = ('reviewed',)
    
    def has_add_permission(self, request):
        return False


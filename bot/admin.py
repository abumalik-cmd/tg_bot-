from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import GlobalLesson
from .forms import ScheduleSelectionForm, LessonAddForm


@admin.register(GlobalLesson)
class GlobalLessonAdmin(admin.ModelAdmin):
    """Админка для модели GlobalLesson"""
    
    list_display = ('grade', 'letter', 'get_day_display', 'number', 'subject')
    list_filter = ('grade', 'letter', 'day')
    search_fields = ('subject',)
    ordering = ('grade', 'letter', 'day', 'number')
    
    def get_urls(self):
        """Добавляем кастомный URL для быстрого добавления расписания"""
        urls = super().get_urls()
        custom_urls = [
            path('quick-add/', self.admin_site.admin_view(self.quick_add_view), name='bot_globallesson_quick_add'),
        ]
        return custom_urls + urls
    
    def quick_add_view(self, request):
        """View для быстрого добавления расписания"""
        
        # Обработка удаления урока
        if request.method == 'POST' and 'delete_lesson' in request.POST:
            lesson_id = request.POST.get('lesson_id')
            try:
                lesson = GlobalLesson.objects.get(id=lesson_id)
                lesson_info = f'{lesson.number}. {lesson.subject}'
                lesson.delete()
                messages.success(request, f'Урок "{lesson_info}" успешно удален')
            except GlobalLesson.DoesNotExist:
                messages.error(request, 'Урок не найден')
            return redirect('admin:bot_globallesson_quick_add')
        
        # Обработка сброса выбора
        if request.method == 'POST' and 'reset_selection' in request.POST:
            request.session.pop('schedule_grade', None)
            request.session.pop('schedule_letter', None)
            request.session.pop('schedule_day', None)
            messages.info(request, 'Выбор сброшен')
            return redirect('admin:bot_globallesson_quick_add')
        
        # Инициализация форм
        selection_form = ScheduleSelectionForm(request.POST if 'select_schedule' in request.POST else None)
        
        # Получаем текущий выбор из сессии
        current_grade = request.session.get('schedule_grade')
        current_letter = request.session.get('schedule_letter')
        current_day = request.session.get('schedule_day')
        
        # Обработка выбора класса/буквы/дня (Шаг 1)
        if request.method == 'POST' and 'select_schedule' in request.POST:
            if selection_form.is_valid():
                request.session['schedule_grade'] = selection_form.cleaned_data['grade']
                request.session['schedule_letter'] = selection_form.cleaned_data['letter']
                request.session['schedule_day'] = int(selection_form.cleaned_data['day'])
                messages.success(request, 'Параметры выбраны. Теперь можете добавлять уроки.')
                return redirect('admin:bot_globallesson_quick_add')
        
        # Получаем обновленные значения после сохранения
        current_grade = request.session.get('schedule_grade')
        current_letter = request.session.get('schedule_letter')
        current_day = request.session.get('schedule_day')
        
        # Переменные для шага 2
        lessons = []
        add_form = None
        day_name = ''
        
        # Если выбор сделан, показываем шаг 2
        if all([current_grade, current_letter, current_day]):
            # Получаем существующие уроки
            lessons = GlobalLesson.objects.filter(
                grade=current_grade,
                letter=current_letter,
                day=current_day
            ).order_by('number')
            
            # Определяем следующий номер урока
            next_number = 1
            if lessons.exists():
                max_number = lessons.order_by('-number').first().number
                next_number = max_number + 1
            
            # Инициализируем форму добавления урока
            add_form = LessonAddForm(
                request.POST if 'add_lesson' in request.POST else None,
                next_number=next_number
            )
            
            # Обработка добавления урока (Шаг 2)
            if request.method == 'POST' and 'add_lesson' in request.POST:
                if add_form.is_valid():
                    number = add_form.cleaned_data['number']
                    subject = add_form.cleaned_data['subject']
                    
                    # Проверяем, существует ли уже урок с таким номером
                    existing_lesson = GlobalLesson.objects.filter(
                        grade=current_grade,
                        letter=current_letter,
                        day=current_day,
                        number=number
                    ).first()
                    
                    if existing_lesson:
                        # Если урок существует, предлагаем перезаписать
                        old_subject = existing_lesson.subject
                        existing_lesson.subject = subject
                        existing_lesson.save()
                        messages.warning(
                            request,
                            f'Урок №{number} перезаписан: "{old_subject}" → "{subject}"'
                        )
                    else:
                        # Создаем новый урок
                        GlobalLesson.objects.create(
                            grade=current_grade,
                            letter=current_letter,
                            day=current_day,
                            number=number,
                            subject=subject
                        )
                        messages.success(request, f'Урок №{number} "{subject}" успешно добавлен')
                    
                    return redirect('admin:bot_globallesson_quick_add')
            
            # Получаем название дня
            day_dict = dict(GlobalLesson.DAY_CHOICES)
            day_name = day_dict.get(current_day, '')
        
        # Подготовка контекста для шаблона
        context = {
            'title': 'Быстрое добавление расписания',
            'selection_form': selection_form,
            'add_form': add_form,
            'lessons': lessons,
            'current_grade': current_grade,
            'current_letter': current_letter,
            'current_day': current_day,
            'day_name': day_name,
            'has_selection': all([current_grade, current_letter, current_day]),
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        
        return render(request, 'admin/bot/globallesson/quick_add.html', context)
    
    def changelist_view(self, request, extra_context=None):
        """Добавляем кнопку быстрого добавления в список уроков"""
        extra_context = extra_context or {}
        extra_context['show_quick_add_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

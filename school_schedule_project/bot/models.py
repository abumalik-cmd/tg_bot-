from django.db import models


class AdminSettings(models.Model):
    contact = models.CharField(max_length=100, default="@Abumalik08", verbose_name="Контакт")
    
    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки"
    
    def __str__(self):
        return f"Контакт: {self.contact}"


class Student(models.Model):
    telegram_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    
    GRADE_CHOICES = [(i, str(i)) for i in range(1, 12)]
    LETTER_CHOICES = [('А', 'А'), ('Б', 'Б'), ('В', 'В'), ('Г', 'Г')]
    
    grade = models.IntegerField(choices=GRADE_CHOICES, null=True, blank=True, verbose_name="Класс")
    letter = models.CharField(max_length=1, choices=LETTER_CHOICES, null=True, blank=True, verbose_name="Буква")
    use_global = models.BooleanField(default=True, verbose_name="Глобальное расписание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Зарегистрирован")
    
    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
    
    def __str__(self):
        if self.grade and self.letter:
            return f"{self.name} ({self.grade}{self.letter})"
        return self.name


class GlobalLesson(models.Model):
    DAY_CHOICES = [(1, 'ПН'), (2, 'ВТ'), (3, 'СР'), (4, 'ЧТ'), (5, 'ПТ')]
    
    grade = models.IntegerField(verbose_name='Класс')
    letter = models.CharField(max_length=1, verbose_name='Буква')
    day = models.IntegerField(choices=DAY_CHOICES, verbose_name='День недели')
    number = models.IntegerField(verbose_name='Номер урока')
    subject = models.CharField(max_length=100, verbose_name='Предмет')
    
    class Meta:
        unique_together = ['grade', 'letter', 'day', 'number']
        verbose_name = 'Глобальный урок'
        verbose_name_plural = 'Глобальные уроки'
        ordering = ['grade', 'letter', 'day', 'number']
    
    def __str__(self):
        return f'{self.grade}{self.letter} - {self.get_day_display()} - {self.number}. {self.subject}'


class PersonalLesson(models.Model):
    DAY_CHOICES = [(1, 'ПН'), (2, 'ВТ'), (3, 'СР'), (4, 'ЧТ'), (5, 'ПТ')]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='personal_lessons', verbose_name="Ученик")
    day = models.IntegerField(choices=DAY_CHOICES, verbose_name='День недели')
    number = models.IntegerField(verbose_name='Номер урока')
    subject = models.CharField(max_length=100, verbose_name='Предмет')
    
    class Meta:
        unique_together = ['student', 'day', 'number']
        ordering = ['student', 'day', 'number']
        verbose_name = "Личный урок"
        verbose_name_plural = "Личные уроки"
    
    def __str__(self):
        return f"{self.student.name} - {self.get_day_display()} {self.number}. {self.subject}"

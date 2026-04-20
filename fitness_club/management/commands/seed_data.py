"""
Management command: python manage.py seed_data

Seeds the database with realistic test data for the Fitness Club API.
"""
import random
from datetime import timedelta, date

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from fitness_club.models import Trainer, MemberProfile, Membership, TrainingClass, Booking


TRAINER_DATA = [
    {'first_name': 'Алексей',   'last_name': 'Смирнов',   'spec': 'crossfit',   'exp': 7,  'rate': 2500},
    {'first_name': 'Мария',     'last_name': 'Волкова',   'spec': 'yoga',       'exp': 5,  'rate': 2000},
    {'first_name': 'Дмитрий',   'last_name': 'Козлов',    'spec': 'boxing',     'exp': 10, 'rate': 3000},
    {'first_name': 'Анна',      'last_name': 'Новикова',  'spec': 'pilates',    'exp': 4,  'rate': 1800},
    {'first_name': 'Сергей',    'last_name': 'Морозов',   'spec': 'strength',   'exp': 8,  'rate': 2800},
    {'first_name': 'Екатерина', 'last_name': 'Павлова',   'spec': 'stretching', 'exp': 3,  'rate': 1600},
]

MEMBER_DATA = [
    {'first_name': 'Иван',    'last_name': 'Петров',    'goal': 'muscle_gain', 'gender': 'M'},
    {'first_name': 'Ольга',   'last_name': 'Кузнецова', 'goal': 'weight_loss', 'gender': 'F'},
    {'first_name': 'Павел',   'last_name': 'Соколов',   'goal': 'endurance',   'gender': 'M'},
    {'first_name': 'Наталья', 'last_name': 'Лебедева',  'goal': 'flexibility', 'gender': 'F'},
    {'first_name': 'Роман',   'last_name': 'Попов',     'goal': 'health',      'gender': 'M'},
    {'first_name': 'Юлия',    'last_name': 'Захарова',  'goal': 'sport',       'gender': 'F'},
    {'first_name': 'Артём',   'last_name': 'Николаев',  'goal': 'muscle_gain', 'gender': 'M'},
    {'first_name': 'Светлана','last_name': 'Орлова',    'goal': 'weight_loss', 'gender': 'F'},
]

CLASS_NAMES = [
    ('CrossFit WOD', 'crossfit', 4),
    ('Йога: утреннее расслабление', 'yoga', 1),
    ('Бокс для начинающих', 'boxing', 2),
    ('Пилатес: осанка и кор', 'pilates', 2),
    ('Силовая: грудь и трицепс', 'strength', 3),
    ('Глубокая растяжка', 'stretching', 1),
    ('CrossFit: олимпийский подъём', 'crossfit', 5),
    ('Йога: баланс и гибкость', 'yoga', 3),
    ('Бокс: спарринг', 'boxing', 4),
    ('Пилатес: продвинутый', 'pilates', 4),
    ('Силовая: ноги и ягодицы', 'strength', 3),
    ('Утренняя растяжка', 'stretching', 1),
]


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными для Fitness Club API'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('🏋️  Наполнение базы данных...'))

        # ── Тренеры ──────────────────────────────────
        self.stdout.write('  → Создаём тренеров...')
        trainers = []
        for i, td in enumerate(TRAINER_DATA):
            username = f"trainer_{td['last_name'].lower()}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': td['first_name'],
                    'last_name': td['last_name'],
                    'email': f"{username}@fitnessclub.com",
                    'is_staff': False,
                }
            )
            user.set_password('trainer123')
            user.save()

            trainer, _ = Trainer.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': td['spec'],
                    'experience_years': td['exp'],
                    'hourly_rate': td['rate'],
                    'bio': f"Опытный тренер по направлению {td['spec']} с {td['exp']} годами практики.",
                    'is_active': True,
                }
            )
            trainers.append(trainer)
        self.stdout.write(self.style.SUCCESS(f'     ✔ Создано тренеров: {len(trainers)}'))

        # ── Участники ─────────────────────────────────
        self.stdout.write('  → Создаём участников...')
        members = []
        for md in MEMBER_DATA:
            username = f"member_{md['last_name'].lower()}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': md['first_name'],
                    'last_name': md['last_name'],
                    'email': f"{username}@mail.com",
                }
            )
            user.set_password('member123')
            user.save()

            profile, _ = MemberProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone': f'+7 (9{random.randint(10,99)}) {random.randint(100,999)}-{random.randint(10,99)}-{random.randint(10,99)}',
                    'gender': md['gender'],
                    'goal': md['goal'],
                    'weight_kg': random.randint(55, 100),
                    'height_cm': random.randint(160, 190),
                    'date_of_birth': date(random.randint(1985, 2000), random.randint(1, 12), random.randint(1, 28)),
                }
            )
            members.append(profile)
        self.stdout.write(self.style.SUCCESS(f'     ✔ Создано участников: {len(members)}'))

        # ── Абонементы ────────────────────────────────
        self.stdout.write('  → Создаём абонементы...')
        plans = ['basic', 'standard', 'premium', 'annual']
        prices = {'basic': 2990, 'standard': 7490, 'premium': 12990, 'annual': 19990}
        durations = {'basic': 30, 'standard': 90, 'premium': 180, 'annual': 365}
        memberships_created = 0
        for member in members:
            if not member.memberships.exists():
                plan = random.choice(plans)
                start = date.today() - timedelta(days=random.randint(0, 30))
                Membership.objects.create(
                    member=member,
                    plan=plan,
                    status='active',
                    start_date=start,
                    end_date=start + timedelta(days=durations[plan]),
                    price_paid=prices[plan],
                    visits_left=None,
                )
                memberships_created += 1
        self.stdout.write(self.style.SUCCESS(f'     ✔ Создано абонементов: {memberships_created}'))

        # ── Занятия ───────────────────────────────────
        self.stdout.write('  → Создаём расписание занятий...')
        spec_to_trainer = {}
        for trainer in trainers:
            spec_to_trainer.setdefault(trainer.specialization, []).append(trainer)

        classes = []
        now = timezone.now()
        for i, (name, spec, diff) in enumerate(CLASS_NAMES):
            # Занятия: часть в прошлом, часть в будущем
            delta_days = (i - 4) * 2
            delta_hours = [9, 11, 13, 15, 17, 19][i % 6]
            scheduled = now.replace(hour=delta_hours, minute=0, second=0, microsecond=0) + timedelta(days=delta_days)

            matched_trainers = spec_to_trainer.get(spec, trainers)
            trainer = random.choice(matched_trainers)

            cls, created = TrainingClass.objects.get_or_create(
                name=name,
                scheduled_at=scheduled,
                defaults={
                    'trainer': trainer,
                    'difficulty': diff,
                    'capacity': random.choice([10, 15, 20, 25]),
                    'duration_minutes': random.choice([45, 60, 75, 90]),
                    'room': random.choice(['Зал A', 'Зал B', 'Зал C', 'Бассейн', 'Ринг']),
                    'price': random.choice([0, 0, 0, 500, 700]),
                    'description': f'Групповое занятие по направлению {spec}. Уровень сложности: {diff}.',
                }
            )
            if created:
                classes.append(cls)

        self.stdout.write(self.style.SUCCESS(f'     ✔ Создано занятий: {len(classes)}'))

        # ── Записи на занятия ─────────────────────────
        self.stdout.write('  → Создаём записи участников на занятия...')
        bookings_created = 0
        all_classes = list(TrainingClass.objects.all())
        for member in members:
            sample_classes = random.sample(all_classes, min(3, len(all_classes)))
            for cls in sample_classes:
                if cls.spots_available > 0:
                    if not Booking.objects.filter(member=member, training_class=cls).exists():
                        is_past = cls.scheduled_at < now
                        Booking.objects.create(
                            member=member,
                            training_class=cls,
                            status=random.choice(['attended', 'no_show']) if is_past else 'confirmed',
                            rating=random.randint(3, 5) if is_past else None,
                            review='Отличное занятие!' if is_past and random.random() > 0.5 else '',
                        )
                        bookings_created += 1

        self.stdout.write(self.style.SUCCESS(f'     ✔ Создано записей: {bookings_created}'))

        # ── Итог ──────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅  База данных успешно заполнена!'))
        self.stdout.write('')
        self.stdout.write('📌  Тестовые аккаунты:')
        self.stdout.write('    Суперпользователь: admin / admin  (создайте через createsuperuser)')
        self.stdout.write('    Тренер:            trainer_смирнов / trainer123')
        self.stdout.write('    Участник:          member_петров / member123')
        self.stdout.write('')
        self.stdout.write('🌐  Swagger UI: http://localhost:8000/swagger/')

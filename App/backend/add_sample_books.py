"""
Script to add 100 sample books to the database
Run this script from the backend directory: python add_sample_books.py
"""
import sys
import os
import random
from datetime import datetime

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Flask app context for database operations
from app import create_app
app = create_app()

from app.services.book_service import BookService
from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository

# Sample data for generating books
SAMPLE_TITLES = [
    "Война и мир", "Преступление и наказание", "Мастер и Маргарита", "Анна Каренина",
    "Братья Карамазовы", "Идиот", "Евгений Онегин", "Мертвые души", "Отцы и дети",
    "Герой нашего времени", "Обломов", "Капитанская дочка", "Дубровский",
    "Горе от ума", "Ревизор", "Гроза", "Вишневый сад", "Чайка", "Три сестры",
    "Бесприданница", "На дне", "Старуха Изергиль", "Макар Чудра", "Челкаш",
    "Двенадцать", "Доктор Живаго", "Тихий Дон", "Судьба человека", "Они сражались за Родину",
    "Белая гвардия", "Собачье сердце", "Роковые яйца", "Дни Турбиных",
    "Записки юного врача", "Морфий", "Бег", "Иван Васильевич", "Театральный роман",
    "Жизнь и судьба", "За правое дело", "В окопах Сталинграда", "Молодая гвардия",
    "Повесть о настоящем человеке", "Василий Теркин", "Дом на набережной",
    "Москва-Петушки", "Пушкинский дом", "Школа для дураков", "Между собакой и волком",
    "Омон Ра", "Generation П", "Чапаев и Пустота", "Empire V", "Ампир В",
    "t", "Любовь к трем апельсинам", "Священная книга оборотня", "ДПП (NN)",
    "Философия Java", "Чистый код", "Рефакторинг", "Паттерны проектирования",
    "Архитектура компьютера", "Алгоритмы и структуры данных", "Искусство программирования",
    "Грокаем алгоритмы", "Вы не знаете JS", "Eloquent JavaScript", "Python для всех",
    "Автоматизация рутинных задач", "Изучаем Python", "Fluent Python", "Effective Python",
    "Гарри Поттер и философский камень", "Гарри Поттер и тайная комната",
    "Гарри Поттер и узник Азкабана", "Гарри Поттер и кубок огня",
    "Гарри Поттер и орден Феникса", "Гарри Поттер и принц-полукровка",
    "Гарри Поттер и дары смерти", "Властелин колец", "Хоббит", "Сильмариллион",
    "Игра престолов", "Битва королей", "Буря мечей", "Пир стервятников", "Танец с драконами",
    "1984", "Скотный двор", "Повелитель мух", "451 градус по Фаренгейту",
    "Убить пересмешника", "Великий Гэтсби", "Старик и море", "По ком звонит колокол",
    "Прощай, оружие!", "И восходит солнце", "За рекой, в тени деревьев"
]

SAMPLE_AUTHORS = [
    "Лев Толстой", "Федор Достоевский", "Михаил Булгаков", "Антон Чехов",
    "Александр Пушкин", "Николай Гоголь", "Иван Тургенев", "Михаил Лермонтов",
    "Иван Гончаров", "Александр Островский", "Максим Горький", "Александр Блок",
    "Сергей Есенин", "Владимир Маяковский", "Борис Пастернак", "Михаил Шолохов",
    "Василий Гроссман", "Виктор Некрасов", "Александр Твардовский", "Юрий Трифонов",
    "Венедикт Ерофеев", "Андрей Битов", "Саша Соколов", "Виктор Пелевин",
    "Брайан Керниган", "Роберт Мартин", "Мартин Фаулер", "Эндрю Таненбаум",
    "Дональд Кнут", "Адитья Бхаргава", "Кайл Симпсон", "Мари Хавербеке",
    "Эрик Мэтиз", "Марк Лутц", "Лучано Рамальо", "Бретт Слаткин",
    "Джоан Роулинг", "Джон Толкин", "Джордж Мартин", "Джордж Оруэлл",
    "Уильям Голдинг", "Рэй Брэдбери", "Харпер Ли", "Фрэнсис Скотт Фицджеральд",
    "Эрнест Хемингуэй", "Джек Лондон", "Марк Твен", "Эдгар Аллан По",
    "Говард Лавкрафт", "Стивен Кинг", "Агата Кристи", "Артур Конан Дойль"
]

SAMPLE_CATEGORIES = [
    "Классическая литература", "Современная проза", "Фантастика", "Фэнтези",
    "Детектив", "Триллер", "Роман", "Повесть", "Рассказ", "Поэзия",
    "Драматургия", "Программирование", "Компьютерные науки", "Алгоритмы",
    "Базы данных", "Веб-разработка", "Мобильная разработка", "Машинное обучение",
    "История", "Философия", "Психология", "Экономика", "Политика",
    "Научная фантастика", "Ужасы", "Приключения", "Биография", "Мемуары"
]

SAMPLE_DESCRIPTIONS = [
    "Классическое произведение русской литературы, которое затрагивает глубокие философские вопросы.",
    "Захватывающий роман о судьбе человека в сложные времена.",
    "Произведение, которое заставляет задуматься о смысле жизни и человеческих ценностях.",
    "Увлекательная история с неожиданными поворотами сюжета.",
    "Книга, которая изменила представление о литературе своего времени.",
    "Глубокий психологический роман о внутреннем мире человека.",
    "Эпическое произведение, охватывающее целую эпоху.",
    "Мастерски написанная история о любви и предательстве.",
    "Произведение, которое стало символом целого поколения.",
    "Классика жанра, обязательная к прочтению.",
    "Практическое руководство для разработчиков всех уровней.",
    "Подробное описание современных подходов к программированию.",
    "Книга, которая поможет освоить новые технологии.",
    "Комплексное руководство по разработке программного обеспечения."
]

SAMPLE_ISBN_PREFIXES = ["978-5-", "978-0-", "978-1-", "978-3-"]

def generate_book_id(existing_ids):
    """Generate a unique book ID"""
    max_num = 0
    for book_id in existing_ids:
        if book_id.startswith('B'):
            try:
                num = int(book_id[1:])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    
    new_num = max_num + 1
    return f"B{new_num:04d}"

def get_or_create_author(author_name):
    """Get existing author or create new one"""
    authors = AuthorRepository.search(author_name)
    for author in authors:
        if author.full_name.lower() == author_name.lower():
            return author
    
    # Create new author
    from app.models.author import Author
    new_author = Author(full_name=author_name)
    if AuthorRepository.create(new_author):
        return AuthorRepository.find_by_id(new_author.id)
    return None

def add_sample_books(count=100):
    """Add sample books to the database"""
    print(f"Начинаем добавление {count} книг в базу данных...")
    
    # Get existing book IDs
    existing_books, _ = BookRepository.find_all()  # Returns tuple (books, total_count)
    existing_ids = [book.id for book in existing_books]
    
    added_count = 0
    failed_count = 0
    
    for i in range(count):
        try:
            # Generate book data
            book_id = generate_book_id(existing_ids)
            existing_ids.append(book_id)
            
            title = random.choice(SAMPLE_TITLES)
            # Sometimes add subtitle
            if random.random() < 0.3:
                subtitle = f"Часть {random.randint(1, 3)}"
            else:
                subtitle = None
            
            # Select 1-2 authors
            num_authors = random.choice([1, 1, 1, 2])  # Mostly 1 author, sometimes 2
            author_names = random.sample(SAMPLE_AUTHORS, num_authors)
            
            # Get or create authors
            authors_info = []
            for author_name in author_names:
                author = get_or_create_author(author_name)
                if author:
                    authors_info.append({
                        'name': author.full_name,
                        'wikipedia_url': None
                    })
            
            if not authors_info:
                print(f"  Пропуск книги {book_id}: не удалось создать авторов")
                failed_count += 1
                continue
            
            category = random.choice(SAMPLE_CATEGORIES)
            description = random.choice(SAMPLE_DESCRIPTIONS)
            
            # Generate ISBN
            isbn = f"{random.choice(SAMPLE_ISBN_PREFIXES)}{random.randint(100000, 999999)}-{random.randint(0, 9)}"
            
            # Generate publication year (between 1800 and 2023)
            publication_year = random.randint(1800, 2023)
            
            # Generate copies (1-5)
            total_copies = random.randint(1, 5)
            available_copies = random.randint(0, total_copies)
            
            # Create book data
            book_data = {
                'id': book_id,
                'title': title,
                'subtitle': subtitle,
                'description': description,
                'publication_year': publication_year,
                'isbn': isbn,
                'total_copies': total_copies,
                'available_copies': available_copies,
                'author': ', '.join([a['name'] for a in authors_info]),  # Legacy field
                'author_names': [a['name'] for a in authors_info],
                'authors_info': authors_info,
                'category': category,
                'covers': []  # No covers for sample books
            }
            
            # Create book
            success, message = BookService.create_book(book_data)
            
            if success:
                added_count += 1
                if (added_count + failed_count) % 10 == 0:
                    print(f"  Добавлено: {added_count}, Ошибок: {failed_count}")
            else:
                failed_count += 1
                print(f"  Ошибка при добавлении книги {book_id}: {message}")
                
        except Exception as e:
            failed_count += 1
            print(f"  Исключение при добавлении книги: {e}")
    
    print(f"\nГотово!")
    print(f"Успешно добавлено: {added_count} книг")
    print(f"Ошибок: {failed_count}")

if __name__ == "__main__":
    # Run within Flask app context
    with app.app_context():
        # Add books
        add_sample_books(100)


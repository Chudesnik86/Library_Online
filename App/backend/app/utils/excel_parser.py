"""
Excel file parser for importing books
"""
from typing import List, Dict, Tuple
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


def parse_books_excel(file_path: str) -> Tuple[List[Dict], List[str]]:
    """
    Parse Excel file and extract book data
    
    Expected Excel format:
    - First row: Headers (Title, Author, ISBN, Category, Total Copies, Available Copies)
    - Following rows: Book data
    
    Args:
        file_path: Path to Excel file
    
    Returns:
        Tuple of (books_data: List[Dict], errors: List[str])
    """
    books_data = []
    errors = []
    
    try:
        workbook = load_workbook(file_path, data_only=True)
        sheet = workbook.active
        
        # Find header row (first row with data)
        header_row = None
        for row_idx, row in enumerate(sheet.iter_rows(min_row=1, max_row=10, values_only=False), start=1):
            values = [cell.value for cell in row if cell.value]
            if any(val and isinstance(val, str) and val.lower() in ['title', 'название', 'название книги'] for val in values):
                header_row = row_idx
                break
        
        if not header_row:
            errors.append("Не найдена строка заголовков. Убедитесь, что первая строка содержит заголовки.")
            return books_data, errors
        
        # Read headers
        headers = {}
        header_cells = sheet[header_row]
        for col_idx, cell in enumerate(header_cells, start=1):
            if cell.value:
                header_text = str(cell.value).strip().lower()
                # Map various header names to standard fields
                if any(x in header_text for x in ['title', 'название', 'название книги', 'книга']):
                    headers['title'] = col_idx
                elif any(x in header_text for x in ['author', 'автор', 'автор книги']):
                    headers['author'] = col_idx
                elif any(x in header_text for x in ['isbn']):
                    headers['isbn'] = col_idx
                elif any(x in header_text for x in ['category', 'категория', 'жанр', 'genre']):
                    headers['category'] = col_idx
                elif any(x in header_text for x in ['description', 'описание', 'описание книги']):
                    headers['description'] = col_idx
                elif any(x in header_text for x in ['cover', 'обложка', 'cover image', 'изображение', 'image', 'url']):
                    headers['cover_image'] = col_idx
                elif any(x in header_text for x in ['total', 'всего', 'total copies', 'всего экземпляров']):
                    headers['total_copies'] = col_idx
                elif any(x in header_text for x in ['available', 'доступно', 'available copies', 'доступно экземпляров']):
                    headers['available_copies'] = col_idx
        
        if 'title' not in headers:
            errors.append("Не найдена колонка с названием книги. Убедитесь, что в файле есть колонка 'Title' или 'Название'.")
            return books_data, errors
        
        # Read data rows
        for row_idx, row in enumerate(sheet.iter_rows(min_row=header_row + 1, values_only=False), start=header_row + 1):
            # Skip empty rows
            if not any(cell.value for cell in row):
                continue
            
            book_data = {}
            
            # Extract title (required)
            title_cell = row[headers['title'] - 1]
            title = str(title_cell.value).strip() if title_cell.value else None
            
            if not title or title.lower() in ['none', 'null', '']:
                errors.append(f"Строка {row_idx}: Отсутствует название книги")
                continue
            
            book_data['title'] = title
            
            # Extract author (optional)
            if 'author' in headers:
                author_cell = row[headers['author'] - 1]
                author = str(author_cell.value).strip() if author_cell.value else None
                if author and author.lower() not in ['none', 'null', '']:
                    book_data['author'] = author
            
            # Extract ISBN (optional)
            if 'isbn' in headers:
                isbn_cell = row[headers['isbn'] - 1]
                isbn = str(isbn_cell.value).strip() if isbn_cell.value else None
                if isbn and isbn.lower() not in ['none', 'null', '']:
                    book_data['isbn'] = isbn
            
            # Extract category (optional)
            if 'category' in headers:
                category_cell = row[headers['category'] - 1]
                category = str(category_cell.value).strip() if category_cell.value else None
                if category and category.lower() not in ['none', 'null', '']:
                    book_data['category'] = category
            
            # Extract description (optional)
            if 'description' in headers:
                desc_cell = row[headers['description'] - 1]
                description = str(desc_cell.value).strip() if desc_cell.value else None
                if description and description.lower() not in ['none', 'null', '']:
                    book_data['description'] = description
            
            # Extract cover image URL (optional)
            if 'cover_image' in headers:
                cover_cell = row[headers['cover_image'] - 1]
                cover_image = str(cover_cell.value).strip() if cover_cell.value else None
                if cover_image and cover_image.lower() not in ['none', 'null', '']:
                    book_data['cover_image'] = cover_image
            
            # Extract total copies (optional, default 1)
            if 'total_copies' in headers:
                total_cell = row[headers['total_copies'] - 1]
                try:
                    total = int(total_cell.value) if total_cell.value else 1
                    book_data['total_copies'] = max(1, total)
                except (ValueError, TypeError):
                    book_data['total_copies'] = 1
            else:
                book_data['total_copies'] = 1
            
            # Extract available copies (optional, default = total_copies)
            if 'available_copies' in headers:
                available_cell = row[headers['available_copies'] - 1]
                try:
                    available = int(available_cell.value) if available_cell.value else book_data['total_copies']
                    book_data['available_copies'] = max(0, min(available, book_data['total_copies']))
                except (ValueError, TypeError):
                    book_data['available_copies'] = book_data['total_copies']
            else:
                book_data['available_copies'] = book_data['total_copies']
            
            books_data.append(book_data)
        
        if not books_data:
            errors.append("Не найдено ни одной книги в файле. Убедитесь, что данные начинаются со второй строки.")
        
    except Exception as e:
        errors.append(f"Ошибка при чтении файла: {str(e)}")
    
    return books_data, errors


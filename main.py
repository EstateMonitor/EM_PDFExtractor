import os

import fitz  # импортируем библиотеку pymupdf
import matplotlib.colors as mcolors


def highlight_rect(rect, colour_name, page):
    colour = mcolors.to_rgb(colour_name)  # По умолчанию черный цвет
    page.draw_rect(rect, color=colour, fill_opacity=0.1)  # Размечаем область выше рисунка


def select_extract_data(rect, colour_name, page):
    textbox = page.get_textbox(rect).strip()
    highlight_rect(rect, colour_name, page)
    return textbox


def validate_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Ошибка: Файл '{pdf_path}' не существует")
    if os.path.getsize(pdf_path) == 0:
        raise ValueError(f"Ошибка: Файл '{pdf_path}' пустой")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise IOError(f"Ошибка: ошибка открытия файла '{pdf_path}': {e}")
    if not doc.is_pdf:
        raise ValueError(f"Ошибка: Файл '{pdf_path}' не является PDF")
    if doc.needs_pass:
        raise PermissionError(f"Ошибка: Файл '{pdf_path}' заблокирован паролем")
    return doc


def highlight_sorted_drawings(pdf_path, output_path):
    validation_result = validate_pdf(pdf_path)
    if isinstance(validation_result, str):
        print(validation_result)
        return
    doc = validation_result

    drawings_dict = {}
    try:
        # Пройдемся по всем страницам документа
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Получаем все рисунки на странице
            drawings = page.get_drawings()
            # Сохраняем информацию о каждом рисунке
            for drawing in drawings:
                rect = drawing['rect']
                height = round(rect.height, 1)
                if height == 3:  # Проверка, чтобы высота рисунка была равна 3
                    if height not in drawings_dict:
                        drawings_dict[height] = []
                    drawings_dict[height].append((page_num, rect))
    # TODO: когда будет добавлено логгирование то сделать обработку следующим способом
    # except fitz.FitzError as e:
    #     logging.error(f"Ошибка: ошибка обработки страниц в файле '{pdf_path}': {e}")
    #     raise
    except Exception as e:
        print(f"Ошибка: ошибка обработки страниц в файле '{pdf_path}': {e}")
        raise

    # Сортируем ключи словаря по высоте
    sorted_heights = sorted(drawings_dict.keys())

    # Список цветов для выделения (RGB)
    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]
    color_count = len(colors)

    # Создаем словарь смещений для каждого поля
    offsets = {
        "company_name": fitz.Rect(90, -15, -130, 0),
        "start_date": fitz.Rect(-65, 5, -740, 35),
        "start_time": fitz.Rect(-8, 5, -695, 35),
        "end_date": fitz.Rect(37, 5, -650, 35),
        "end_time": fitz.Rect(82, 5, -605, 35),
        "downtime_hours": fitz.Rect(127, 5, -565, 35),
        "factory_number": fitz.Rect(168, 5, -515, 35),
        "registration_number": fitz.Rect(222, 5, -455, 35)
    }

    for index, height in enumerate(sorted_heights):
        color = colors[index % color_count]  # Выбираем цвет из списка
        for page_num, rect in drawings_dict[height]:
            page = doc.load_page(page_num)
            highlight = fitz.Rect(rect)
            highlight_rect(highlight, color, page)
            print(f"Page {page_num + 1}: Rectangle {rect} with height {height} highlighted in color {color}")

            for field, offset in offsets.items():
                extracted_data = select_extract_data(rect + offset,
                                                     'green' if field == 'company_name' else 'red' if 'date' in field or field == 'downtime_hours' else 'blue' if 'time' in field else 'magenta' if field == 'factory_number' else 'yellow',
                                                     page)
                print(f"Extracted {field}: {extracted_data}")

    # TODO: вынести сохранение с проверкой в отдельную функцию (сделать, когда добавится log)
    try:
        # Сохраняем документ с изменениями
        doc.save(output_path)
        print(f"Modified PDF saved as: {output_path}")
    except Exception as e:
        print(f"Ошибка: ошибка сохранения файла '{output_path}': {e}")


# Укажите путь к вашему PDF файлу и путь для сохранения измененного PDF
pdf_path = '1.pdf'
output_path = 'highlighted_sorted_drawings.pdf'

highlight_sorted_drawings(pdf_path, output_path)

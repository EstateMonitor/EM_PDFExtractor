import fitz  # импортируем библиотеку pymupdf
import matplotlib.colors as mcolors

def highlight_rect(rect, colour_name, page):
    colour = mcolors.to_rgb(colour_name)  # По умолчанию черный цвет
    page.draw_rect(rect, color=colour, fill_opacity=0.1)  # Размечаем область выше рисунка

def select_extract_data(rect, colour_name, page):
    textbox = page.get_textbox(rect).strip()
    highlight_rect(rect, colour_name, page)
    return textbox


def highlight_sorted_drawings(pdf_path, output_path):
    # Открываем документ
    doc = fitz.open(pdf_path)
    drawings_dict = {}
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

    # Сортируем ключи словаря по высоте
    sorted_heights = sorted(drawings_dict.keys())

    # Список цветов для выделения (RGB)
    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]
    color_count = len(colors)

    # Пройдемся по отсортированным высотам и выделим рисунки соответствующим цветом
    for index, height in enumerate(sorted_heights):
        color = colors[index % color_count]  # Выбираем цвет из списка
        for page_num, rect in drawings_dict[height]:
            page = doc.load_page(page_num)
            highlight = fitz.Rect(rect)
            page.draw_rect(highlight, color=color, fill_opacity=0.5)
            print(f"Page {page_num + 1}: Rectangle {rect} with height {height} highlighted in color {color}")

            # company_name of OOO
            company_name = select_extract_data(fitz.Rect(rect.x0 + 90, rect.y0 - 15, rect.x1 - 130, rect.y1), 'green', page)
            print(f"Extracted company_name above rectangle: {company_name}")

            # TODO: to scan for the information in the loop for several lifts
            start_date = select_extract_data(fitz.Rect(rect.x0 - 65, rect.y0 + 5, rect.x1 - 740, rect.y1 + 35), 'red', page)
            print(f"Extracted start_date in rectangle: {start_date}")

            start_time = select_extract_data(fitz.Rect(rect.x0 - 8, rect.y0 + 5, rect.x1 - 695, rect.y1 + 35), 'blue', page)
            print(f"Extracted start_time in rectangle: {start_time}")

            end_date = select_extract_data(fitz.Rect(rect.x0 + 37, rect.y0 + 5, rect.x1 - 650, rect.y1 + 35), 'red', page)
            print(f"Extracted end_date in rectangle: {end_date}")

            end_time = select_extract_data(fitz.Rect(rect.x0 + 82, rect.y0 + 5, rect.x1 - 605, rect.y1 + 35), 'blue', page)
            print(f"Extracted end_time in rectangle: {end_time}")

            downtime_hours = select_extract_data(fitz.Rect(rect.x0 + 127, rect.y0 + 5, rect.x1 - 565, rect.y1 + 35), 'red', page)
            print(f"Extracted end_date in rectangle: {downtime_hours}")

            factory_number = select_extract_data(fitz.Rect(rect.x0 + 168, rect.y0 + 5, rect.x1 - 515, rect.y1 + 35), 'magenta', page)
            print(f"Extracted end_date in rectangle: {factory_number}")

            registration_number = select_extract_data(fitz.Rect(rect.x0 + 222, rect.y0 + 5, rect.x1 - 455, rect.y1 + 35), 'yellow', page)
            print(f"Extracted end_date in rectangle: {registration_number}")


    # Сохраняем документ с изменениями
    doc.save(output_path)
    print(f"Modified PDF saved as: {output_path}")


# Укажите путь к вашему PDF файлу и путь для сохранения измененного PDF
pdf_path = "1.pdf"
output_path = "highlighted_sorted_drawings.pdf"

highlight_sorted_drawings(pdf_path, output_path)

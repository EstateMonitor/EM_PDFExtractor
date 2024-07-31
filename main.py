import fitz  # импортируем библиотеку pymupdf


def select_extract_data(x0, y0, x1, y1, r, g, b, page):
    rect = fitz.Rect(x0, y0, x1, y1)
    textbox = page.get_textbox(rect).strip()
    page.draw_rect(rect, color=(r, g, b), fill_opacity=0.1)  # Размечаем область выше рисунка
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
            company_name = select_extract_data(rect.x0 + 90, rect.y0 - 15, rect.x1 - 130, rect.y1, 0,1,0, page)
            print(f"Extracted company_name above rectangle: {company_name}")

            # TODO: to scan for the information in the loop for several lifts
            # start_date selection
            start_date = select_extract_data(rect.x0 - 65, rect.y0 + 5, rect.x1 - 740, rect.y1 + 35, 1,0,0, page)
            print(f"Extracted start_date above rectangle: {start_date}")

    # Сохраняем документ с изменениями
    doc.save(output_path)
    print(f"Modified PDF saved as: {output_path}")


# Укажите путь к вашему PDF файлу и путь для сохранения измененного PDF
pdf_path = "1.pdf"
output_path = "highlighted_sorted_drawings.pdf"

highlight_sorted_drawings(pdf_path, output_path)

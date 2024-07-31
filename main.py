import fitz  # импортируем библиотеку pymupdf

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
            if height == 3:  # Проверка, чтобы высота рисунка была больше 3
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

            # organization_name of OOO
            top_rect = fitz.Rect(rect.x0 + 90, rect.y0 - 15, rect.x1 - 130, rect.y1)
            organization_name = page.get_textbox(top_rect)
            page.draw_rect(top_rect, color=(0, 1, 0), fill_opacity=0.1)  # Размечаем область выше рисунка
            print(f"Extracted organization_name above rectangle: {organization_name}")

    # Сохраняем документ с изменениями
    doc.save(output_path)
    print(f"Modified PDF saved as: {output_path}")

# Укажите путь к вашему PDF файлу и путь для сохранения измененного PDF
pdf_path = "1.pdf"
output_path = "highlighted_sorted_drawings.pdf"

highlight_sorted_drawings(pdf_path, output_path)

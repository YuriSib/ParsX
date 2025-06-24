from html.parser import HTMLParser


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = []

    def handle_starttag(self, tag, attrs):
        if tag in ('br', 'p', 'li'):
            self.data.append('\n')

    def handle_data(self, d):
        self.data.append(d)

    def get_data(self):
        return ''.join(self.data).strip()


def strip_tags(html):
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_data()


def get_finished_desc(html: str):
    block = ("""\n\n____________________________________________________________ \n"""
             """Срок доставки - 2 часа с момента заказа. (с 9:00 до 18:00) \n"""
             """Стоимость доставки по городу - 250 рублей \n"""
             """При заказе на сумму от 1500 р. - доставка по городу бесплатно \n"""
             """_____________________________________________________________ \n"""
             """Для получения более подробной информации и заказа, нажмите "Перейти" """)

    desc = strip_tags(html)

    return desc + block


if __name__ == "__main__":
    html_desc = """<ul version="2"><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Вариант установки: на раковину</li><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Вид излива: жесткий</li><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Материал корпуса: пластик, силумин</li><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Наличие индикатора температуры: да</li><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Параметр сети: В220</li><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Способ монтажа: на гайку</li><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Способ нагрева: электрический</li><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Тип водонагревателя: проточный</li><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Тип электроподключения: в розетку</li><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Установка водонагревателя: горизонтальная</li><li style="text-align: var(--alignment_unorderedList_RichEditor_Base, left); list-style-position: var(--listStylePosition_unorderedList_RichEditor_Base, outside);">Цвет: белый</li></ul>"""

    final_desc = get_finished_desc(html_desc)
    print(final_desc)



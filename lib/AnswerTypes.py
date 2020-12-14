class AnswerType:
    # Абстрактный типа ответа
    def __init__(self, id, description):
        self.id = id
        self.description = description

    def get_id(self):
        return self.id

    def get_description(self):
        return self.description


class ManualInput(AnswerType):
    # Ручной ввод
    def __init__(self):
        super().__init__(0, "Ручной ввод")


class SingleAnswer(AnswerType):
    # Выбор одного ответа
    def __init__(self):
        super().__init__(1, "Выбор одного ответа")


class MultiplyAnswer(AnswerType):
    # Выбор нескольких ответов
    def __init__(self):
        super().__init__(2, "Выбор нескольких ответов")

# Список нужен для удобного обращения к типу по его ID. Enum в этом случае не так удобно использовать
ANSWER_TYPES = [ManualInput(), SingleAnswer(), MultiplyAnswer()]
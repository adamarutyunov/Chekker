class AnswerType:
    def __init__(self, id, description):
        self.id = id
        self.description = description

    def get_id(self):
        return self.id

    def get_description(self):
        return self.description


class ManualInput(AnswerType):
    def __init__(self):
        super().__init__(0, "Ручной ввод")


class SingleAnswer(AnswerType):
    def __init__(self):
        super().__init__(1, "Выбор одного ответа")


class MultiplyAnswer(AnswerType):
    def __init__(self):
        super().__init__(2, "Выбор нескольких ответов")


ANSWER_TYPES = [ManualInput(), SingleAnswer(), MultiplyAnswer()]
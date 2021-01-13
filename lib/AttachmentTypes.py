class AttachmentType:
    # Абстрактный тип вложения
    def __init__(self, id, description):
        self.id = id
        self.description = description

    def get_id(self):
        return self.id

    def get_description(self):
        return self.description


class ImageAttachment(AttachmentType):
    # Ручной ввод
    def __init__(self):
        super().__init__(1, "Изображение")


# Список нужен для удобного обращения к типу по его ID. Enum в этом случае не так удобно использовать
ATTACHMENT_TYPES = [AttachmentType, ImageAttachment]
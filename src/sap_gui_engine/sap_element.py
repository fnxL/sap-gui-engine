import logging

logger = logging.getLogger(__name__)


class SAPElement:
    def __init__(self, element: any):
        self.element = element
        self.type = element.type
        self.text = element.text
        self.changeable = element.changeable

    def set_value(self, value: any):
        try:
            self.element.text = str(value)
        except Exception as e:
            logger.error(f"Error setting value for element {self.element.name}: {e}")
            raise ValueError(f"Error setting value for element {self.element.name}")

    def get_value(self):
        return self.text

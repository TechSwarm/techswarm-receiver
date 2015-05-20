class Usart:
    """
    Usart class implement communication with usart device, receiving records and photos
    """
    def get(self):
        try:
            return input()
        except:
            pass
        # for test only
        # todo: replace with real usart receiving

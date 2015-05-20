class Usart:
    """
    Usart class implement communication with usart device, receiving records and photos
    """
    def get(self):
        try:
            return input()
        except:
            while True:
                pass
        # for test only
        # todo: replace with real usart receiving

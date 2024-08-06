class MockTOTP:

    def __init__(self, key):
        pass

    def verify(self, passcode):
        if passcode == str(123456):
            return True
        return False
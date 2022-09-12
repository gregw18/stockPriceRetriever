"""
Singleton metaclass
V0.1, December 27, 2022, GAW
Taken from https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
"""

class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance
    
    def __call_(self):
        raise TypeError('Singletons must be accessed through`instance()`.')
    
    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

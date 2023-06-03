class Test:
    def __init__(self, x):
        self._x = x
        self.maxx = 15

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if self._x > self.maxx:
            self._x = self.maxx
            print("Exceeded")


obj = Test(1)
obj.x = 16
print(obj)

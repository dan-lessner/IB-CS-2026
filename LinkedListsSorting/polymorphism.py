class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("Subclasses must implement this method")
    
class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):  
    def speak(self):
        return f"{self.name} says Meow!"

class Fox(Animal):  
    def speak(self):
        return f"{self.name} says Ring-ding-ding!"
    
Pluto = Dog("Pluto")
Mittens = Cat("Mittens")
Sly = Fox("Sly")
print(Pluto.speak())  # Output: Pluto says Woof!   
print(Mittens.speak())  # Output: Mittens says Meow!
print(Sly.speak())  # Output: Sly says Ring-ding-ding!
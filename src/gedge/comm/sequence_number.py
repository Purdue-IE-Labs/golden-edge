from dataclasses import dataclass, field

@dataclass
class SequenceNumber:
    value: int = field(default=0)
    MAX = 255

    def __int__(self):
        return self.value
    
    def __bytes__(self):
        return bytes(str(self.value), encoding="utf-8")
    
    def increment(self):
        self.value = (self.value + 1) % self.MAX
        return self.value
    

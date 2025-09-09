#import abc
from Error import Error
from Consts import Consts

class TValue(): 
	def __init__(self) -> None:
		self.value = None

	def setMemory(self, memory=None): return self.exceptionError(f"The 'setMemory({memory})' method not suported on the {Error.classNameOf(self)} class!") #raise NotImplementedError
	def add(self, other): return self.exceptionError(f"The 'add({self}{Consts.PLUS}{other})' method not suported on the {Error.classNameOf(self)} class!") #raise NotImplementedError
	def sub(self, other): return self.exceptionError(f"The 'sub({self}{Consts.MINUS}{other})' method not suported on the {Error.classNameOf(self)} class!") #raise NotImplementedError
	def mult(self, other): return self.exceptionError(f"The 'mult({self}{Consts.MUL}{other})' method not suported on the {Error.classNameOf(self)} class!") #raise NotImplementedError
	def div(self, other): return self.exceptionError(f"The 'div({self}{Consts.DIV}{other})' method not suported on the {Error.classNameOf(self)} class!") #raise NotImplementedError
	def pow(self, other): return self.exceptionError(f"The 'pow({self}{Consts.POW}{other})' method not suported on the {Error.classNameOf(self)} class!") #raise NotImplementedError
	def copy(self): return self.exceptionError(f"The 'copy()' method not suported on the {Error.classNameOf(self)} class!") #raise NotImplementedError
	
	def exceptionError(self, error_msn: str): return None, Error(f"{Error.runTimeError}: {error_msn}")

	def __eq__(self, value: object) -> bool:
		if isinstance(value, TValue):
			return self.value == value.value
		return False
	
	def __hash__(self) -> int:
		return hash(self.value)

class TNumber(TValue):
	def __init__(self, value):
		self.value = value
		self.setMemory()
	def setMemory(self, memory=None):
		self.memory = memory
		return self
	def add(self, other):
		if isinstance(other, TNumber):
			return TNumber(self.value + other.value).setMemory(self.memory), None
		return super().add(other)
	def sub(self, other):
		if isinstance(other, TNumber):
			return TNumber(self.value - other.value).setMemory(self.memory), None
		return super().sub(other)
	def mult(self, other):
		if isinstance(other, TNumber):
			return TNumber(self.value * other.value).setMemory(self.memory), None
		return super().mult(other)
	def div(self, other):
		if isinstance(other, TNumber):
			if other.value == 0:
				return self.exceptionError("Divisao por zero")
			return TNumber(self.value / other.value).setMemory(self.memory), None
		return super().div(other)
	def pow(self, other):
		if isinstance(other, TNumber):
			return TNumber(self.value ** other.value).setMemory(self.memory), None
		return super().pow(other)
	def copy(self):
		copy = TNumber(self.value)
		copy.setMemory(self.memory)
		return copy	
	def __repr__(self):
		return str(self.value)
class TString(TValue):
	def __init__(self, value):
		self.value = value
		self.setMemory()
	def setMemory(self, memory=None):
		self.memory = memory
		return self
	def add(self, other):
		if isinstance(other, TString):
			return TString(self.value + other.value).setMemory(self.memory), None
		return super().add(other)
	def copy(self):
		copy = TString(self.value)
		copy.setMemory(self.memory)
		return copy		
	def __repr__(self):
		return f'"{str(self.value)}"'
##############################
class TList(TValue):
	def __init__(self, value):
		self.value = value
		self.setMemory()
	def setMemory(self, memory=None):
		self.memory = memory
		return self
	def add(self, other):
		if isinstance(other, TList):
			return TList(self.value + other.value).setMemory(self.memory), None
		return super().add(other)
	def copy(self):
		copy = TList(self.value)
		copy.setMemory(self.memory)
		return copy	
	
	def __repr__(self):
		return f"{str(self.value)}"
##############################

class TTuple(TValue):
    def __init__(self, value):
        self.value = tuple(value)  # sempre tupla imutável!
        self.setMemory()
    def setMemory(self, memory=None):
        self.memory = memory
        return self
    def copy(self):
        copy = TTuple(self.value)
        copy.setMemory(self.memory)
        return copy
    def __repr__(self):
        return f"{self.value}"


class TFunction(TValue):
    def __init__(self, params, body, closure=None):
        self.params = params[:]         # lista de nomes (str)
        self.body = body                # nó AST do corpo (Visitor)
        self.closure = closure or {}    # captura (simples) do ambiente
    def setMemory(self, memory=None):
        self.memory = memory
        return self
    def copy(self):
        c = TFunction(self.params, self.body, self.closure.copy())
        c.setMemory(self.memory)
        return c
    def __repr__(self):
        return f"<fn({', '.join(self.params)})>"
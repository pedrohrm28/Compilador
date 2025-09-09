from Error import Error

class TValue(): 
    def __init__(self) -> None:
        self.value = None
    def setMemory(self, memory=None): 
        return self.exceptionError(f"The 'setMemory(memory)' method is not implemented on the {Error.classNameOf(self)} class!")
    def add(self, other):  return self.exceptionError(f"The 'add(self, other)' method is not implemented on the {Error.classNameOf(self)} class!")
    def sub(self, other):  return self.exceptionError(f"The 'sub(self, other)' method is not implemented on the {Error.classNameOf(self)} class!")
    def mult(self, other): return self.exceptionError(f"The 'mult(self, other)' method is not implemented on the {Error.classNameOf(self)} class!")
    def div(self, other):  return self.exceptionError(f"The 'div(self, other)' method is not implemented on the {Error.classNameOf(self)} class!")
    def pow(self, other):  return self.exceptionError(f"The 'pow(self, other)' method is not implemented on the {Error.classNameOf(self)} class!")
    def copy(self):        return self.exceptionError(f"The 'copy()' method is not implemented on the {Error.classNameOf(self)} class!")
    def exceptionError(self, error_msn: str):
        return None, Error(f"{Error.runTimeError}: {error_msn}")
    def __eq__(self, value: object) -> bool:
        if isinstance(value, TValue): return self.value == value.value
        return False
    def __hash__(self) -> int: return hash(self.value)

class TNumber(TValue):
    def __init__(self, value):
        self.value = value; self.setMemory()
    def setMemory(self, memory=None): self.memory = memory; return self
    def add(self, other):
        if isinstance(other, TNumber): return TNumber(self.value + other.value).setMemory(self.memory), None
        if isinstance(other, TString): return TString(str(self.value) + other.value).setMemory(self.memory), None
        return super().add(other)
    def sub(self, other):
        if isinstance(other, TNumber): return TNumber(self.value - other.value).setMemory(self.memory), None
        return super().sub(other)
    def mult(self, other):
        if isinstance(other, TNumber): return TNumber(self.value * other.value).setMemory(self.memory), None
        return super().mult(other)
    def div(self, other):
        if isinstance(other, TNumber):
            if other.value == 0: return None, Error(f"{Error.runTimeError}: divisao por zero")
            return TNumber(self.value / other.value).setMemory(self.memory), None
        return super().div(other)
    def pow(self, other):
        if isinstance(other, TNumber): return TNumber(self.value ** other.value).setMemory(self.memory), None
        return super().pow(other)
    def copy(self): 
        c = TNumber(self.value); c.setMemory(self.memory); return c
    def __repr__(self): return str(self.value)

class TString(TValue):
    def __init__(self, value):
        self.value = value; self.setMemory()
    def setMemory(self, memory=None): self.memory = memory; return self
    def add(self, other):
        if isinstance(other, TString): return TString(self.value + other.value).setMemory(self.memory), None
        if isinstance(other, TNumber): return TString(self.value + str(other.value)).setMemory(self.memory), None
        return super().add(other)
    def copy(self):
        c = TString(self.value); c.setMemory(self.memory); return c
    def __repr__(self): return f'"{self.value}"'

class TList(TValue):
    def __init__(self, value):
        self.value = list(value); self.setMemory()
    def setMemory(self, memory=None): self.memory = memory; return self
    def copy(self):
        c = TList([v.copy() if isinstance(v, TValue) else v for v in self.value]); c.setMemory(self.memory); return c
    def __repr__(self): return f"{self.value}"

class TTuple(TValue):
    def __init__(self, value):
        self.value = tuple(value); self.setMemory()
    def setMemory(self, memory=None): self.memory = memory; return self
    def copy(self):
        c = TTuple(self.value); c.setMemory(self.memory); return c
    def __repr__(self): return f"{self.value}"

# --- Objetos (dicionario) ---
class TObject(TValue):
    def __init__(self, mapping):
        self.value = dict(mapping); self.setMemory()
    def setMemory(self, memory=None): self.memory = memory; return self
    def copy(self):
        # deep copy raso (copia valores TValue)
        c = TObject({k: (v.copy() if isinstance(v, TValue) else v) for k, v in self.value.items()})
        c.setMemory(self.memory); return c
    def __repr__(self):
        keys = ", ".join(self.value.keys())
        return f"{{{keys}}}"

# --- Funções ---
class TFunction(TValue):
    def __init__(self, params, body, closure=None):
        self.params = params[:]; self.body = body; self.closure = dict(closure or {}); self.setMemory()
    def setMemory(self, memory=None): self.memory = memory; return self
    def copy(self):
        c = TFunction(self.params, self.body, self.closure.copy()); c.setMemory(self.memory); return c
    def __repr__(self): return f"<fn({', '.join(self.params)})>"

# --- Built-ins (nativas) ---
class TBuiltin(TValue):
    def __init__(self, name, impl):
        self.name = name
        self.impl = impl  # (operator, [args]) -> (TValue, Error|None)
        self.setMemory()
    def setMemory(self, memory=None): self.memory = memory; return self
    def copy(self): return self  # imutavel/compartilhado
    def apply(self, operator, args):
        return self.impl(operator, args)
    def __repr__(self): return f"<builtin {self.name}>"

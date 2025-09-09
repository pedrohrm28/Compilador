from Consts import Consts
from SemanticVisitor import TNumber
from Error import Error

####################################### Tabela de simbolos (Symbol Table) #######################################
class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def get(self, name):
        return self.symbols.get(name, None)

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


####################################### Gerente de Memoria #######################################
class MemoryManager:
    singleton = None

    def __init__(self):
        if MemoryManager.singleton is not None:
            raise Exception(f"{Error.singletonMsg(self)}.instanceOfMemoryManager(resetErrors=True)'!")
        self.value = None
        self.error = None
        MemoryManager.singleton = self
        self.configSymbolTable()

    def configSymbolTable(self):
        # escopo global
        self.symbolTable = SymbolTable()
        self.symbolTable.set(Consts.NULL, TNumber(0))  # 'null' -> 0
        # pilha de escopos: [global]
        self.tables = [self.symbolTable]

    # ---------- Escopos ----------
    def push_scope(self, closure=None):
        tbl = SymbolTable()
        if closure:
            tbl.symbols.update(closure)
        self.tables.append(tbl)

    def pop_scope(self):
        if len(self.tables) > 1:
            self.tables.pop()
        else:
            self.fail(Error("Pop de escopo global"))

    def snapshot_env(self):
        # snapshot raso do topo atual
        return self.tables[-1].symbols.copy()

    # ---------- Símbolos ----------
    def get(self, name):
        for tbl in reversed(self.tables):
            v = tbl.get(name)
            if v is not None:
                return v
        return None

    def set(self, name, value):
        self.tables[-1].set(name, value)

    # ---------- Protocolo de execução ----------
    def registry(self, rtr):
        if rtr.error:
            self.error = rtr.error
        return rtr.value

    def success(self, value):
        self.value = value
        return self

    def fail(self, error):
        self.error = error
        return self

    @staticmethod
    def resetSingletonError():
        MemoryManager.singleton.error = None
        return MemoryManager.singleton

    @staticmethod
    def instanceOfMemoryManager(resetErrors=True):
        if MemoryManager.singleton is None:
            MemoryManager.singleton = MemoryManager()
        return MemoryManager.resetSingletonError() if resetErrors else MemoryManager.singleton

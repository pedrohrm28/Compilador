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
        if name in self.symbols:
            del self.symbols[name]

####################################### Gerente de Memoria #######################################
class MemoryManager:
    singleton = None

    def __init__(self):
        self.tables = [SymbolTable()]   # escopo global
        self.value = None
        self.error = None

    # --- API de escopo ---
    def push_scope(self, closure=None):
        tbl = SymbolTable()
        if closure:
            tbl.symbols.update(closure)
        self.tables.append(tbl)

    def pop_scope(self):
        if len(self.tables) <= 1:
            self.fail(Error("Pop de escopo global"))
            return
        self.tables.pop()

    def snapshot_env(self):
        # snapshot raso do topo atual
        return self.tables[-1].symbols.copy()

    # Alias para compatibilidade com codigo existente
    @property
    def symbolTable(self):
        return self.tables[-1]

    # --- API de simbolos ---
    def get(self, name):
        for tbl in reversed(self.tables):
            v = tbl.get(name)
            if v is not None:
                return v
        return None

    def set(self, name, value):
        self.tables[-1].set(name, value)

    # --- protocolo de execucao/erros ---
    def registry(self, manager_or_value):
        # aceita MemoryManager retornado de visitas aninhadas OU valor direto
        if isinstance(manager_or_value, MemoryManager):
            if manager_or_value.error:
                self.error = manager_or_value.error
                return None
            self.value = manager_or_value.value
            return self.value
        else:
            self.value = manager_or_value
            return self.value

    def success(self, value):
        self.value = value
        return self

    def fail(self, error):
        self.error = error
        return self

    @staticmethod    
    def resetSingletonError():
        if MemoryManager.singleton is None:
            MemoryManager.singleton = MemoryManager()
        MemoryManager.singleton.error = None
        return MemoryManager.singleton
    
    @staticmethod
    def instanceOfMemoryManager(resetErrors=True):
        if MemoryManager.singleton is None:
            MemoryManager.singleton = MemoryManager()
        return MemoryManager.resetSingletonError() if resetErrors else MemoryManager.singleton

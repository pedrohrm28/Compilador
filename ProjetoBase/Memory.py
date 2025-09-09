from Error import Error

class SymbolTable:
    def __init__(self): self.symbols = {}
    def get(self, name): return self.symbols.get(name, None)
    def set(self, name, value): self.symbols[name] = value
    def remove(self, name): 
        if name in self.symbols: del self.symbols[name]

class MemoryManager:
    singleton = None

    def __init__(self):
        self.tables = [SymbolTable()]   # escopo global
        self.value = None
        self.error = None
        self._install_builtins()        # NEW

    # --- Escopos ---
    def push_scope(self, closure=None):
        tbl = SymbolTable()
        if closure: tbl.symbols.update(closure)
        self.tables.append(tbl)

    def pop_scope(self):
        if len(self.tables) <= 1:
            self.fail(Error("Pop de escopo global")); return
        self.tables.pop()

    def snapshot_env(self):
        return self.tables[-1].symbols.copy()

    @property
    def symbolTable(self): return self.tables[-1]

    # --- Símbolos ---
    def get(self, name):
        for tbl in reversed(self.tables):
            v = tbl.get(name)
            if v is not None: return v
        return None

    def set(self, name, value):
        self.tables[-1].set(name, value)

    # --- protocolo ---
    def registry(self, manager_or_value):
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
        self.value = value; return self

    def fail(self, error):
        self.error = error; return self

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

    # --------------- Built-ins ---------------
    def _install_builtins(self):
        # import lazy para evitar ciclos
        from TValue import TNumber, TString, TList, TTuple, TObject, TBuiltin, TFunction
        from Error import Error

        def _truthy(v):
            if isinstance(v, TNumber): return v.value != 0
            if isinstance(v, TString): return len(v.value) > 0
            if isinstance(v, (TList, TTuple, TObject)): return len(v.value) > 0
            if isinstance(v, (TBuiltin, TFunction)): return True
            return v is not None

        def _len(op, args):
            if len(args) != 1:
                return None, Error("len espera 1 argumento")
            a = args[0]
            if isinstance(a, (TList, TTuple)): n = len(a.value)
            elif isinstance(a, TString): n = len(a.value)
            elif isinstance(a, TObject): n = len(a.value)
            else:
                return None, Error("len: tipo nao suportado")
            return TNumber(n).setMemory(op), None

        def _count(op, args):
            # count(list) -> len(list)
            if len(args) == 1:
                return _len(op, args)
            # count(list, fn) -> quantos elementos tornam fn(elem) truthy
            if len(args) == 2:
                lst, pred = args[0], args[1]
                if not isinstance(lst, TList):
                    return None, Error("count: primeiro argumento deve ser lista")
                cnt = 0
                for el in lst.value:
                    # chamar pred(el)
                    if isinstance(pred, TFunction):
                        op.push_scope(pred.closure)
                        op.set(pred.params[0], el)
                        out = op.registry(pred.body.visit(op))
                        op.pop_scope()
                        if op.error: return None, op.error
                        if _truthy(out): cnt += 1
                    elif isinstance(pred, TBuiltin):
                        out, err = pred.apply(op, [el])
                        if err: return None, err
                        if _truthy(out): cnt += 1
                    else:
                        return None, Error("count: segundo argumento deve ser funcao")
                return TNumber(cnt).setMemory(op), None
            return None, Error("count espera 1 ou 2 argumentos")

        # instalar
        self.set('len',      TBuiltin('len', _len))
        self.set('count',    TBuiltin('count', _count))
        self.set('count_by', TBuiltin('count_by', _count)) 

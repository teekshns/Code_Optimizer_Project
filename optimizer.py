import ast

class CodeOptimizer:
    def __init__(self, code):
        self.original_code = code.strip().split('\n')
        self.variables = {}
        self.tac = []
        self.optimized_code = []

    def generate_tac(self):
        tac_lines = []
        temp_count = 1

        for line in self.original_code:
            line = line.strip()
            if '=' in line and not line.startswith('print'):
                var, expr = line.split('=', 1)
                var, expr = var.strip(), expr.strip()

                try:
                    # Try to evaluate the expression
                    value = eval(expr, {}, self.variables)
                    self.variables[var] = value
                    tac_lines.append(f"{var} = {value}")
                except:
                    # Handle variables in the expression
                    for v in self.variables:
                        expr = expr.replace(v, str(self.variables[v]))
                    tac_lines.append(f"{var} = {expr}")
                    try:
                        self.variables[var] = eval(expr)
                    except:
                        self.variables[var] = None
            else:
                tac_lines.append(line)
        self.tac = tac_lines

    def constant_folding(self):
        folded = []
        for line in self.tac:
            if '=' in line and not line.startswith('print'):
                var, expr = line.split('=', 1)
                var, expr = var.strip(), expr.strip()
                try:
                    val = eval(expr)
                    folded.append(f"{var} = {val}")
                    self.variables[var] = val
                except:
                    folded.append(line)
            else:
                folded.append(line)
        self.tac = folded

    def constant_propagation(self):
        propagated = []
        for line in self.tac:
            if '=' in line and not line.startswith('print'):
                var, expr = line.split('=', 1)
                var, expr = var.strip(), expr.strip()
                for k, v in self.variables.items():
                    if v is not None:
                        expr = expr.replace(k, str(v))
                propagated.append(f"{var} = {expr}")
                try:
                    self.variables[var] = eval(expr)
                except:
                    self.variables[var] = None
            else:
                propagated.append(line)
        self.tac = propagated

    def dead_code_elimination(self):
        used_vars = set()
        final_lines = []
        reversed_lines = list(reversed(self.tac))

        for line in reversed_lines:
            if line.startswith('print'):
                tokens = line.replace('print(', '').replace(')', '').split()
                used_vars.update(tokens)
                final_lines.append(line)
            elif '=' in line:
                var, expr = line.split('=', 1)
                var, expr = var.strip(), expr.strip()
                if var in used_vars:
                    final_lines.append(line)
                    used_vars.update(expr.split())
        self.tac = list(reversed(final_lines))

    def optimize(self, options):
        self.generate_tac()

        if "constant_folding" in options:
            self.constant_folding()
        if "constant_propagation" in options:
            self.constant_propagation()
        if "dead_code_elimination" in options:
            self.dead_code_elimination()

        # Generate final optimized Python code
        self.optimized_code = self.tac

    def get_tac(self):
        return '\n'.join(self.tac)

    def get_optimized_code(self):
        return '\n'.join(self.optimized_code)

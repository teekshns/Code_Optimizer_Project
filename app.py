from flask import Flask, render_template, request
import re

app = Flask(__name__)

def generate_TAC(code_lines):
    tac = []
    const_map = {}

    i = 0
    while i < len(code_lines):
        line = code_lines[i].strip()

        # Unroll simple for-loops for TAC generation
        loop_match = re.match(r"for\s+(\w+)\s+in\s+range\((\d+)\):", line)
        if loop_match:
            var = loop_match.group(1)
            count = int(loop_match.group(2))
            i += 1
            # Check if next line is indented (loop body)
            if i < len(code_lines) and (code_lines[i].startswith("    ") or code_lines[i].startswith("\t")):
                body_line = code_lines[i].strip()
                for iteration in range(count):
                    # Correct replacement of loop variable with iteration value
                    replaced = re.sub(rf'\b{var}\b', str(iteration), body_line)
                    tac.append(replaced)
                i += 1
            else:
                i += 1
            continue

        # Constant folding: var = number op number
        match = re.match(r"^(\w+)\s*=\s*(\d+)\s*([\+\-\*/])\s*(\d+)$", line)
        if match:
            var, left, op, right = match.groups()
            val = eval(f"{left}{op}{right}")
            tac.append(f"{var} = {val}")
            const_map[var] = val
            i += 1
            continue

        # Constant propagation: var = var op number
        match = re.match(r"^(\w+)\s*=\s*(\w+)\s*([\+\-\*/])\s*(\d+)$", line)
        if match:
            var, left, op, right = match.groups()
            if left in const_map:
                val = eval(f"{const_map[left]}{op}{right}")
                tac.append(f"{var} = {val}")
                const_map[var] = val
            else:
                tac.append(line)
            i += 1
            continue

        # Constant propagation: var = number op var
        match = re.match(r"^(\w+)\s*=\s*(\d+)\s*([\+\-\*/])\s*(\w+)$", line)
        if match:
            var, left, op, right = match.groups()
            if right in const_map:
                val = eval(f"{left}{op}{const_map[right]}")
                tac.append(f"{var} = {val}")
                const_map[var] = val
            else:
                tac.append(line)
            i += 1
            continue

        # Simple constant assignment: var = number
        match = re.match(r"^(\w+)\s*=\s*(\d+)$", line)
        if match:
            var, val = match.groups()
            tac.append(line)
            const_map[var] = int(val)
            i += 1
            continue

        # Propagation: var = other_var
        match = re.match(r"^(\w+)\s*=\s*(\w+)$", line)
        if match:
            var, val = match.groups()
            if val in const_map:
                tac.append(f"{var} = {const_map[val]}")
                const_map[var] = const_map[val]
            else:
                tac.append(line)
            i += 1
            continue

        # Pass through any other code (e.g., print)
        tac.append(line)
        i += 1

    return tac

def optimize_TAC(tac):
    used_vars = set()
    # Scan backward to find used vars
    for line in tac[::-1]:
        if "print" in line:
            match = re.findall(r"print\((.*?)\)", line)
            if match:
                used_vars.update(match)
        elif "=" in line:
            var, expr = [x.strip() for x in line.split("=", 1)]
            if var in used_vars:
                used_vars.update(re.findall(r"\w+", expr))
    # Remove assignments to unused vars
    optimized = []
    for line in tac:
        if "=" in line and not line.startswith("print"):
            var = line.split("=")[0].strip()
            if var in used_vars:
                optimized.append(line)
        elif "print" in line:
            optimized.append(line)
        else:
            optimized.append(line)  # Keep lines like loops (for now)
    return optimized

def loop_unroll_TAC(code_lines):
    """
    Detect and unroll simple for loops of form:
    for i in range(N):
        <single statement>
    """
    unrolled = []
    i = 0
    while i < len(code_lines):
        line = code_lines[i].strip()
        loop_match = re.match(r"for\s+(\w+)\s+in\s+range\((\d+)\):", line)
        if loop_match:
            var = loop_match.group(1)
            count = int(loop_match.group(2))
            i += 1
            # Check if next line is indented (loop body)
            if i < len(code_lines) and (code_lines[i].startswith("    ") or code_lines[i].startswith("\t")):
                body_line = code_lines[i].strip()
                # We only handle single line loop bodies for simplicity
                for iteration in range(count):
                    # Replace loop var with iteration value in body_line
                    replaced = re.sub(r'\b' + var + r'\b', str(iteration), body_line)
                    unrolled.append(replaced)
                i += 1
            else:
                # No loop body, just skip
                i += 1
        else:
            unrolled.append(line)
            i += 1
    return unrolled

def suggest_optimization(code_lines):
    suggestion = []
    for line in code_lines:
        if re.search(r"\d+\s*[\+\-\*/]\s*\d+", line):
            suggestion.append("Constant Folding")
        elif re.search(r"\w+\s*=\s*\w+\s*[\+\-\*/]\s*\d+", line):
            suggestion.append("Constant Propagation")
        elif re.match(r"^\w+\s*=\s*\d+$", line):
            suggestion.append("Dead Code Elimination")
        elif re.match(r"for\s+\w+\s+in\s+range\(\d+\):", line):
            suggestion.append("Loop Unrolling")
    if not suggestion:
        return "No optimization suggested"
    return f"{suggestion[0]} might be most effective."

@app.route("/", methods=["GET", "POST"])
def index():
    input_code = ""
    tac_output = ""
    optimized_code = ""
    selected_opts = []
    suggestion = ""

    if request.method == "POST":
        input_code = request.form["code"]
        selected_opts = request.form.getlist("optimizations")
        code_lines = input_code.strip().split("\n")

        # 1. Generate TAC from the original code (no unrolling)
        tac = generate_TAC(code_lines)
        tac_output = "\n".join(tac)

        # 2. Prepare code for optimization (start with original)
        optimized_code_lines = code_lines.copy()

        # 3. Apply loop unrolling ONLY for optimized code
        if "loop_unrolling" in selected_opts:
            optimized_code_lines = loop_unroll_TAC(optimized_code_lines)

        # 4. Apply other optimizations
        optimized = generate_TAC(optimized_code_lines)
        if "dead_code_elimination" in selected_opts:
            optimized = optimize_TAC(optimized)

        optimized_code = "\n".join(optimized)
        suggestion = suggest_optimization(code_lines)

    return render_template("index.html", input_code=input_code,
                           tac_output=tac_output,
                           optimized_code=optimized_code,
                           selected_opts=selected_opts,
                           suggestion=suggestion)

if __name__ == "__main__":
    app.run(debug=True)

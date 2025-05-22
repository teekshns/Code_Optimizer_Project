# Code Optimizer

A web-based tool for visualizing and applying code optimization techniques such as constant folding, constant propagation, dead code elimination, and loop unrolling. The app displays both the Three-Address Code (TAC) and the optimized code for the user’s input.

## Features

- **Constant Folding:** Evaluates constant expressions at compile time.
- **Constant Propagation:** Replaces variables with known constant values.
- **Dead Code Elimination:** Removes code that does not affect the program output.
- **Loop Unrolling:** Expands simple loops for optimization.
- **TAC Generation:** Shows the intermediate Three-Address Code for the input.
- **Optimized Code:** Shows the result after applying selected optimizations.

## Usage

1. **Install dependencies:**
   ```bash
   pip install flask
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser and go to:**
   ```
   http://127.0.0.1:5000/
   ```

4. **Enter your code** in the text area, select the desired optimization techniques, and click "Optimize" to see the TAC and optimized code.

## Example

**Input:**
```python
for i in range(3):
    x = i + 2
```

**TAC Output:**
```
x = 0 + 2
x = 1 + 2
x = 2 + 2
```

**Optimized Code (with constant folding):**
```
x = 2
x = 3
x = 4
```

## Project Structure

```
.
├── app.py              # Main Flask application
├── optimizer.py        # (Optional) Additional optimization logic
├── templates/
│   └── index.html      # Web UI template
├── static/             # Static files (CSS, etc.)
└── requirements.txt    # Python dependencies
```

## Notes

- Only simple, single-line loop bodies are supported for loop unrolling.
- The tool is for educational/demo purposes and does not support all Python syntax.

## License

MIT License

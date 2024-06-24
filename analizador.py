from flask import Flask, request, render_template_string
import re
import ply.lex as lex

app = Flask(__name__)

tokens = [
    'INT', 'ID', 'NUM', 'SYM', 'ERR', 'WHILE', 'DO', 'ENDDO', 'ENDWHILE'
]

t_INT = r'\bint\b'
t_WHILE = r'\bWHILE\b'
t_DO = r'\bDO\b'
t_ENDDO = r'\bENDDO\b'
t_ENDWHILE = r'\bENDWHILE\b'
t_ID = r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'
t_NUM = r'\b\d+\b'
t_SYM = r'[;{}()\[\]=<>!+-/*]'
t_ERR = r'.'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

html_template = '''
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      font-family: 'Open Sans', sans-serif;
      background-color: #c4f8ef;
      color: #333;
      margin: 0;
      padding: 20px;
    }
    h1 {
      text-align: center;
      color: #ffffff;
      margin-bottom: 20px;
    }
    .analyzer-section {
      background-color: #fff;
      padding: 20px;
      border-radius: 5px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      margin-bottom: 30px;
    }
    textarea {
      width: 100%;
      padding: 15px;
      border: 1px solid #dbbdff;
      border-radius: 4px;
      font-size: 16px;
    }
    input[type="submit"] {
      background-color: #dbbdff;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      font-size: 16px;
      margin-top: 10px;
    }
    input[type="submit"]:hover {
      background-color: #dbbdff;
    }
    table {
      width: 100%;
      margin: 20px 0;
      table-layout: fixed;
    }
    th, td {
      border: 1px solid #dbbdff;
      padding: 10px;
      text-align: left;
      word-wrap: break-word;
    }
    th {
      background-color: #dbbdff;
      color: white;
    }
    tr:nth-child(even) {
      background-color: #f8f9fa;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    .lexical-container {
      max-height: 400px;
      overflow-y: auto;
    }
  </style>
  <title>Analizador de Código</title>
</head>
<body>
  <div class="container">
    <h1>Analizador de Código</h1>
    <form method="post" class="analyzer-section">
      <textarea name="code" rows="10">{{ code }}</textarea>
      <input type="submit" value="Analizar">
    </form>
    <div class="row">
      {% if lexical %}
      <div class="col-md-6 analyzer-section">
        <h2>Resultados del Análisis Léxico</h2>
        <div class="lexical-container">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Token</th>
                <th>INT</th>
                <th>ID</th>
                <th>Números</th>
                <th>Símbolos</th>
                <th>WHILE</th>
                <th>DO</th>
                <th>ENDDO</th>
                <th>ENDWHILE</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {% for row in lexical %}
              <tr>
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
                <td>{{ row[2] }}</td>
                <td>{{ row[3] }}</td>
                <td>{{ row[4] }}</td>
                <td>{{ row[5] }}</td>
                <td>{{ row[6] }}</td>
                <td>{{ row[7] }}</td>
                <td>{{ row[8] }}</td>
                <td>{{ row[9] }}</td>
              </tr>
              {% endfor %}
              <tr class="font-weight-bold">
                <td>Total</td>
                <td>{{ total['INT'] }}</td>
                <td>{{ total['ID'] }}</td>
                <td>{{ total['NUM'] }}</td>
                <td>{{ total['SYM'] }}</td>
                <td>{{ total['WHILE'] }}</td>
                <td>{{ total['DO'] }}</td>
                <td>{{ total['ENDDO'] }}</td>
                <td>{{ total['ENDWHILE'] }}</td>
                <td>{{ total['ERR'] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      {% endif %}
      {% if syntactic or semantic %}
      <div class="col-md-6 analyzer-section">
        <h2>Resultados del Análisis Sintáctico</h2>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Sintáctico</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ syntactic }}</td>
            </tr>
          </tbody>
        </table>
        <h2>Resultados del Análisis Semántico</h2>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Semántico</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ semantic }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      {% endif %}
    </div>
  </div>
  <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.3/dist/umd/popper.min.js"></script>
  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
'''

def analyze_lexical(code):
    lexer.input(code)
    results = {'INT': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'WHILE': 0, 'DO': 0, 'ENDDO': 0, 'ENDWHILE': 0, 'ERR': 0}
    rows = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        row = [''] * 10
        if tok.type in results:
            results[tok.type] += 1
            row[list(results.keys()).index(tok.type)] = 'x'
        row[0] = tok.value
        rows.append(row)
    return rows, results

def analyze_syntactic(code):
    errors = []
    lines = code.split('\n')
    open_do = 0
    open_while = 0
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('int'):
            if not re.match(r'int\s+[a-zA-Z_][a-zA-Z_0-9]*\s*=\s*\d+\s*;', stripped_line):
                errors.append(f"Error en declaración de variable: '{stripped_line}'")
        elif stripped_line.startswith('WHILE'):
            if not re.match(r'WHILE\s*\([a-zA-Z_][a-zA-Z_0-9]*\s*==\s*\d+\)', stripped_line):
                errors.append(f"Error en declaración de WHILE: '{stripped_line}'")
            open_while += 1
        elif stripped_line == 'DO':
            open_do += 1
        elif stripped_line == 'ENDDO':
            open_do -= 1
            if open_do < 0:
                errors.append(f"ENDDO sin DO correspondiente: '{stripped_line}'")
        elif stripped_line == 'ENDWHILE':
            open_while -= 1
            if open_while < 0:
                errors.append(f"ENDWHILE sin WHILE correspondiente: '{stripped_line}'")
        elif re.match(r'[a-zA-Z_][a-zA-Z_0-9]*\s*=\s*[^;]+;', stripped_line):
            pass
        else:
            errors.append(f"Error en sintaxis: '{stripped_line}'")

    if open_do != 0:
        errors.append("Desbalanceo de bloques DO y ENDDO.")
    if open_while != 0:
        errors.append("Desbalanceo de bloques WHILE y ENDWHILE.")

    if not errors:
        return "Sintaxis correcta"
    else:
        return " ".join(errors)
    

def analyze_semantic(code):
    errors = []
    variable_types = {}
    lines = code.split('\n')
    for line in lines:
        stripped_line = line.strip().lower()
        if stripped_line.startswith('int'):
            match = re.match(r'int\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*=\s*(\d+)\s*;', stripped_line)
            if match:
                var_name, value = match.groups()
                if var_name in variable_types:
                    errors.append(f"Variable redeclarada: '{var_name}'")
                else:
                    variable_types[var_name] = 'int'
            else:
                errors.append(f"Error en declaración de variable: '{stripped_line}'")
        elif re.match(r'[a-zA-Z_][a-zA-Z_0-9]*\s*=\s*[^;]+;', stripped_line):
            match = re.match(r'([a-zA-Z_][a-zA-Z_0-9]*)\s*=\s*([^;]+);', stripped_line)
            if match:
                var_name, expression = match.groups()
                if var_name not in variable_types:
                    errors.append(f"Variable no declarada antes de la asignación: '{var_name}'")
                for token in re.findall(r'[a-zA-Z_][a-zA-Z_0-9]*', expression):
                    if token not in variable_types and not token.isdigit():
                        errors.append(f"Uso de variable no declarada '{token}' en la expresión '{expression}'")
        elif stripped_line.startswith('while'):
            match = re.match(r'while\s*\(([a-zA-Z_][a-zA-Z_0-9]*)\s*==\s*(\d+)\)', stripped_line)
            if match:
                var_name, value = match.groups()
                if var_name not in variable_types:
                    errors.append(f"Uso de variable no declarada en la condición WHILE: '{var_name}'")

    if not errors:
        return "Uso correcto de las estructuras semánticas"
    else:
        return " ".join(errors)

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ''
    lexical_results = []
    total_results = {'INT': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'WHILE': 0, 'DO': 0, 'ENDDO': 0, 'ENDWHILE': 0, 'ERR': 0}
    syntactic_result = ''
    semantic_result = ''
    if request.method == 'POST':
        code = request.form['code']
        lexical_results, total_results = analyze_lexical(code)
        syntactic_result = analyze_syntactic(code)
        semantic_result = analyze_semantic(code)
    return render_template_string(html_template, code=code, lexical=lexical_results, total=total_results, syntactic=syntactic_result, semantic=semantic_result)

if __name__ == '__main__':
    app.run(debug=True)

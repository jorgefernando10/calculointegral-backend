from flask import Flask, request, jsonify
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import traceback
import os  # <-- ADICIONE ESTA LINHA

app = Flask(__name__)
x = symbols('x')

@app.route('/integral', methods=['POST'])
def calcular_integral():
    try:
        dados = request.json
        expr_str = dados.get('expr', '').strip()
        var_str = dados.get('var', 'x')
        limite_inf = dados.get('a')
        limite_sup = dados.get('b')

        if not expr_str:
            return jsonify({"error": "Expressão não fornecida"}), 400

        expr = parse_expr(expr_str)
        var = symbols(var_str)

        if var not in expr.free_symbols and expr != 0:
            return jsonify({"error": f"Variável '{var_str}' não encontrada."}), 400

        if limite_inf is not None and limite_sup is not None:
            try:
                limite_inf = parse_expr(str(limite_inf))
                limite_sup = parse_expr(str(limite_sup))
                resultado = integrate(expr, (var, limite_inf, limite_sup))
                tipo = "definida"
            except Exception as e:
                return jsonify({"error": f"Erro na integral definida: {str(e)}"}), 400
        else:
            resultado = integrate(expr, var)
            tipo = "indefinida"

        expr_latex = latex(expr)
        result_latex = latex(resultado)

        return jsonify({
            "success": True,
            "tipo": tipo,
            "input": expr_str,
            "input_latex": f"\\int {expr_latex} \\, d{var_str}",
            "result": str(resultado),
            "result_latex": result_latex
        })

    except SyntaxError:
        return jsonify({"error": "Erro de sintaxe na expressão."}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

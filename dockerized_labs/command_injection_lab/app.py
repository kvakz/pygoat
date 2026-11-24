from flask import Flask, render_template, request
import subprocess
import os
import ast
import math
import operator

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"

BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_calculate(expression):
    if not expression or len(expression) > 100:
        raise ValueError("Invalid expression length")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            result = node.value

        elif isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPS:
            result = BINARY_OPS[type(node.op)](
                evaluate(node.left),
                evaluate(node.right)
            )

        elif isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            result = UNARY_OPS[type(node.op)](
                evaluate(node.operand)
            )

        else:
            raise ValueError("Only basic arithmetic is allowed")

        if not math.isfinite(result) or abs(result) > 1_000_000_000:
            raise ValueError("Result exceeds allowed range")

        return result

    return evaluate(tree.body)


@app.route("/")
def index():
    """Main page with command injection lab description"""
    return render_template("index.html")


@app.route("/lab1", methods=["GET", "POST"])
def lab1():
    """Lab 1: Name Server Lookup with Command Injection"""
    if request.method == "POST":
        domain = request.form.get("domain", "")
        os_type = request.form.get("os", "")

        if os_type == "win":
            command = f"nslookup {domain}"
        else:
            command = f"dig {domain}"

        try:
            # Intentionally vulnerable command execution
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            output = stdout.decode("utf-8") + stderr.decode("utf-8")
        except Exception as e:
            output = str(e)

        return render_template("lab1.html", output=output)

    return render_template("lab1.html")


@app.route("/lab2", methods=["GET", "POST"])
def lab2():
    """Lab 2: Python eval() Code Execution"""
    if request.method == "POST":
        try:
            # Intentionally vulnerable eval
            expression = request.form.get("val", "")
            output = safe_calculate(expression)
            return render_template("lab2.html", output=str(output))
        except Exception as e:
            return render_template("lab2.html", output=str(e))
    return render_template("lab2.html")

@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5013, debug=True)

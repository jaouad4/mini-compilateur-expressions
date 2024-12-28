import tkinter as tk
from tkinter import ttk, messagebox
import re


class MathLexer:
    def __init__(self):
        self.tokens = []

    def tokenize(self, text):
        patterns = [
            ('NUMBER', r'\d+(\.\d+)?'),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MULTIPLY', r'\*'),
            ('DIVIDE', r'/'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('WHITESPACE', r'\s+')
        ]

        combined_pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns)
        token_regex = re.compile(combined_pattern)

        self.tokens = []
        for match in token_regex.finditer(text):
            token_type = match.lastgroup
            token_value = match.group()

            if token_type != 'WHITESPACE':
                if token_type == 'NUMBER':
                    token_value = float(token_value)
                self.tokens.append((token_type, token_value))

        return self.tokens


class MathParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self):
        token = self.peek()
        self.pos += 1
        return token

    def parse(self):
        return self.expression()

    def expression(self):
        result = self.term()

        while self.peek() and self.peek()[0] in ['PLUS', 'MINUS']:
            op = self.consume()
            right = self.term()
            if op[0] == 'PLUS':
                result = ('ADD', result, right)
            else:
                result = ('SUB', result, right)

        return result

    def term(self):
        result = self.factor()

        while self.peek() and self.peek()[0] in ['MULTIPLY', 'DIVIDE']:
            op = self.consume()
            right = self.factor()
            if op[0] == 'MULTIPLY':
                result = ('MUL', result, right)
            else:
                result = ('DIV', result, right)

        return result

    def factor(self):
        token = self.peek()
        if token[0] == 'NUMBER':
            self.consume()
            return ('NUM', token[1])
        elif token[0] == 'LPAREN':
            self.consume()
            result = self.expression()
            if not self.peek() or self.peek()[0] != 'RPAREN':
                raise SyntaxError("Parenthèse fermante manquante")
            self.consume()
            return result
        else:
            raise SyntaxError(f"Token inattendu: {token}")


class MathEvaluator:
    @staticmethod
    def evaluate(ast):
        if ast[0] == 'NUM':
            return ast[1]
        elif ast[0] == 'ADD':
            return MathEvaluator.evaluate(ast[1]) + MathEvaluator.evaluate(ast[2])
        elif ast[0] == 'SUB':
            return MathEvaluator.evaluate(ast[1]) - MathEvaluator.evaluate(ast[2])
        elif ast[0] == 'MUL':
            return MathEvaluator.evaluate(ast[1]) * MathEvaluator.evaluate(ast[2])
        elif ast[0] == 'DIV':
            denominator = MathEvaluator.evaluate(ast[2])
            if denominator == 0:
                raise ZeroDivisionError("Division par zéro")
            return MathEvaluator.evaluate(ast[1]) / denominator


class MathCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculatrice - JAOUAD Salah-Eddine")
        self.root.geometry("600x400")

        # Style
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Result.TLabel", font=("Helvetica", 12))

        # Composants
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titre
        title_label = ttk.Label(
            main_frame,
            text="Évaluateur d'expressions mathématiques",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20))

        # Zone de saisie
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Expression:").pack(side=tk.LEFT)
        self.expression_var = tk.StringVar()
        self.expression_entry = ttk.Entry(
            input_frame,
            textvariable=self.expression_var,
            width=50
        )
        self.expression_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # Bouton Calculer
        self.calc_button = ttk.Button(
            main_frame,
            text="Calculer",
            command=self.evaluate_expression
        )
        self.calc_button.pack(pady=(0, 20))

        # Zone des résultats
        result_frame = ttk.LabelFrame(main_frame, text="Résultats", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)

        # Widgets pour afficher les résultats
        ttk.Label(result_frame, text="Tokens:").pack(anchor=tk.W)
        self.tokens_text = tk.Text(result_frame, height=2, wrap=tk.WORD)
        self.tokens_text.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(result_frame, text="AST:").pack(anchor=tk.W)
        self.ast_text = tk.Text(result_frame, height=2, wrap=tk.WORD)
        self.ast_text.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(result_frame, text="Résultat:").pack(anchor=tk.W)
        self.result_label = ttk.Label(result_frame, text="", style="Result.TLabel")
        self.result_label.pack(anchor=tk.W)

    def evaluate_expression(self):
        expression = self.expression_var.get().strip()
        if not expression:
            messagebox.showwarning("Attention", "Veuillez entrer une expression")
            return

        try:
            # Analyse lexicale
            lexer = MathLexer()
            tokens = lexer.tokenize(expression)
            self.tokens_text.delete(1.0, tk.END)
            self.tokens_text.insert(tk.END, str(tokens))

            # Analyse syntaxique
            parser = MathParser(tokens)
            ast = parser.parse()
            self.ast_text.delete(1.0, tk.END)
            self.ast_text.insert(tk.END, str(ast))

            # Évaluation
            result = MathEvaluator.evaluate(ast)
            self.result_label.config(text=f"{result}")

        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.tokens_text.delete(1.0, tk.END)
            self.ast_text.delete(1.0, tk.END)
            self.result_label.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    app = MathCalculatorGUI(root)
    root.mainloop()
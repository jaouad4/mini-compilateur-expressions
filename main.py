import re


class MathLexer:
    def __init__(self):
        self.tokens = []

    def tokenize(self, text):
        # Définition des patterns pour chaque type de token
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

        # Combine tous les patterns en une seule expression régulière
        combined_pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns)
        token_regex = re.compile(combined_pattern)

        # Trouve tous les tokens
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
            self.consume()  # Consomme la parenthèse ouvrante
            result = self.expression()
            if not self.peek() or self.peek()[0] != 'RPAREN':
                raise SyntaxError("Parenthèse fermante manquante")
            self.consume()  # Consomme la parenthèse fermante
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
            return MathEvaluator.evaluate(ast[1]) / MathEvaluator.evaluate(ast[2])


def evaluate_expression(expression):
    print(f"\nÉvaluation de : {expression}")
    try:
        # Analyse lexicale
        lexer = MathLexer()
        tokens = lexer.tokenize(expression)
        print("Tokens:", tokens)

        # Analyse syntaxique
        parser = MathParser(tokens)
        ast = parser.parse()
        print("AST:", ast)

        # Évaluation
        result = MathEvaluator.evaluate(ast)
        print("Résultat:", result)
        return result
    except Exception as e:
        print("Erreur:", str(e))
        return None


# Test des expressions
expressions = [
    "5 + ( 2 * ( 8 - 3 ) )",
    "7 - (3 + 6)/3"
    ""
]

for expr in expressions:
    evaluate_expression(expr)

print("\n")

# Liste des expressions de test couvrant différents cas
test_expressions = [
    # 1. Tests basiques pour chaque opérateur
    "5 + 3",  # Addition simple
    "10 - 4",  # Soustraction simple
    "6 * 2",  # Multiplication simple
    "8 / 2",  # Division simple

    # 2. Tests de priorité des opérateurs sans parenthèses
    "2 + 3 * 4",  # Multiplication prioritaire sur addition
    "10 - 6 / 2",  # Division prioritaire sur soustraction
    "2 * 3 + 4",  # Multiplication avant addition
    "8 / 2 - 1",  # Division avant soustraction

    # 3. Tests avec parenthèses simples
    "(2 + 3) * 4",  # Parenthèses modifiant la priorité
    "8 / (2 + 2)",  # Division par une expression entre parenthèses
    "(5 + 3) - 2",  # Parenthèses en début d'expression
    "4 * (6 - 2)",  # Parenthèses en fin d'expression

    # 4. Tests avec parenthèses imbriquées
    "((2 + 3) * 4)",  # Double parenthèses
    "2 * (3 + (4 - 1))",  # Parenthèses imbriquées à droite
    "(2 * (3 + 4)) - 1",  # Parenthèses imbriquées à gauche
    "((8 + 2) * (3 - 1))",  # Parenthèses multiples

    # 5. Tests avec expressions complexes
    "5 + 2 * 3 - 4 / 2",  # Combinaison d'opérateurs
    "(8 + 2 * 3) / (2 + 2)",  # Expressions complexes avec parenthèses
    "2 * (3 + 4 * (5 - 2)) - 6",  # Expression très imbriquée
    "((4 + 2) * 3 - 6) / 2",  # Combinaison de parenthèses et opérateurs

    # 6. Tests avec nombres décimaux
    "5.5 + 3.2",  # Addition avec décimaux
    "10.5 / 2.5",  # Division avec décimaux
    "(2.5 * 4) + 1.5",  # Parenthèses avec décimaux

    # 7. Tests des cas limites
    "0 + 0",  # Opération avec zéros
    "1 / 0",  # Division par zéro (doit générer une erreur)
    "(((1)))",  # Multiples parenthèses imbriquées
    "5",  # Nombre seul

    # 8. Tests de robustesse
    "  5  +  3  ",  # Espaces supplémentaires
    "5++3",  # Opérateurs répétés (devrait générer une erreur)
    "5 + (3",  # Parenthèse manquante (devrait générer une erreur)
    ")5 + 3(",  # Parenthèses mal placées (devrait générer une erreur)
]


def run_tests():
    print("=== DÉBUT DES TESTS ===\n")
    successes = 0
    failures = 0

    # Résultats attendus pour les expressions valides
    expected_results = {
        "5 + 3": 8,
        "10 - 4": 6,
        "6 * 2": 12,
        "8 / 2": 4,
        "2 + 3 * 4": 14,
        "10 - 6 / 2": 7,
        "2 * 3 + 4": 10,
        "8 / 2 - 1": 3,
        "(2 + 3) * 4": 20,
        "8 / (2 + 2)": 2,
        "(5 + 3) - 2": 6,
        "4 * (6 - 2)": 16,
        "((2 + 3) * 4)": 20,
        "2 * (3 + (4 - 1))": 12,
        "(2 * (3 + 4)) - 1": 13,
        "((8 + 2) * (3 - 1))": 20,
        "5 + 2 * 3 - 4 / 2": 9,
        "(8 + 2 * 3) / (2 + 2)": 3.5,
        "2 * (3 + 4 * (5 - 2)) - 6": 38,
        "((4 + 2) * 3 - 6) / 2": 6,
        "5.5 + 3.2": 8.7,
        "10.5 / 2.5": 4.2,
        "(2.5 * 4) + 1.5": 11.5,
        "0 + 0": 0,
        "5": 5,
        "  5  +  3  ": 8,
    }

    for expr in test_expressions:
        print(f"\nTest de l'expression : {expr}")
        try:
            # Analyse lexicale
            lexer = MathLexer()
            tokens = lexer.tokenize(expr)
            print("Tokens:", tokens)

            # Analyse syntaxique
            parser = MathParser(tokens)
            ast = parser.parse()
            print("AST:", ast)

            # Évaluation
            result = MathEvaluator.evaluate(ast)
            print("Résultat obtenu:", result)

            # Vérification du résultat si disponible
            if expr in expected_results:
                expected = expected_results[expr]
                if abs(result - expected) < 0.0001:  # Comparaison avec tolérance pour les flottants
                    print("✓ Test réussi")
                    successes += 1
                else:
                    print(f"✗ Échec : résultat attendu = {expected}")
                    failures += 1
            else:
                print("! Pas de résultat attendu défini pour cette expression")

        except Exception as e:
            if expr in ["1 / 0", "5++3", "5 + (3", ")5 + 3("]:
                print("✓ Erreur attendue détectée:", str(e))
                successes += 1
            else:
                print("✗ Erreur inattendue:", str(e))
                failures += 1

    print("\n=== RÉSUMÉ DES TESTS ===")
    print(f"Tests réussis : {successes}")
    print(f"Tests échoués : {failures}")
    print(f"Total des tests : {successes + failures}")
    print("=====================")


# Exécution des tests
run_tests()
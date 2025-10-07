# Assignment-7
#Aim:To implement a Propositional Logic Theorem Prover using the Resolution Refutation Method.
#parse->CNF->apply ref resolution->contra if yes->reached goal

#Steps performed by the program:
#Parsing:
#The input formulas are parsed into a syntax tree using recursive descent.
#Conversion to CNF (Conjunctive Normal Form):
#Eliminates implications (A -> B → ~A | B)
#Eliminates equivalence (A <-> B → (A -> B) & (B -> A))
#Applies De Morgan’s laws and simplifies
#Distributes disjunctions over conjunctions
#Produces a list of clauses
#Resolution Process:
#Adds negated goal to the premises
#Repeatedly applies the resolution rule:
#If two clauses contain complementary literals (like P and ~P),
#combine them by removing the complementary pair.
#If an empty clause [] is derived → contradiction → goal is proven.


#Number of premises: just the number of formulas you provide
#Number of clauses:after CNF conversion, including all premises and negated goal.


import re
from typing import List, Set, Tuple, Optional, Union

class PropositionalLogic:
    #Initializes an empty set of propositional variables.
    def __init__(self):
        self.variables = set()

#Defines a tree node representing a logical expression
    class Node:
        def __init__(self, value, left=None, right=None):
            self.value = value
            self.left = left
            self.right = right

#Returns a readable string form of the expression tree.
        def __str__(self):
            if self.left is None and self.right is None:
                return self.value
            elif self.left is not None and self.right is None:  # Negation
                return f"~{self.left}"
            else:
                left_str = f"({self.left})" if self.left and self.left.left and self.left.right else str(self.left)
                right_str = f"({self.right})" if self.right and self.right.left and self.right.right else str(self.right)
                return f"{left_str} {self.value} {right_str}"

    def parse_formula(self, formula_str: str) -> Node:
        """Parse propositional logic formula into tree structure"""
        formula_str = formula_str.replace(' ', '')

        # Tokenize
        tokens = []
        i = 0
        while i < len(formula_str):
            if formula_str[i] in '()~&|':
                tokens.append(formula_str[i])
                i += 1
            elif formula_str[i:i+2] == '->':
                tokens.append('->')
                i += 2
            elif formula_str[i:i+3] == '<->':
                tokens.append('<->')
                i += 3
            elif formula_str[i].isupper():
                tokens.append(formula_str[i])
                self.variables.add(formula_str[i])
                i += 1
            else:
                raise ValueError(f"Invalid character: {formula_str[i]}")
        return self._parse_expression(tokens)

#starts expression parsing.
    def _parse_expression(self, tokens: List[str]) -> Node:
        if not tokens:
            raise ValueError("Empty expression")
        return self._parse_implication(tokens)
#Handles parsing of implication (->) and equivalence (<->) operators.
    def _parse_implication(self, tokens: List[str]) -> Node:
        left = self._parse_disjunction(tokens)
        if tokens and tokens[0] == '->':
            tokens.pop(0)
            right = self._parse_implication(tokens)
            return self.Node('->', left, right)
        elif tokens and tokens[0] == '<->':
            tokens.pop(0)
            right = self._parse_implication(tokens)
            return self.Node('<->', left, right)
        return left
#Handles logical OR (|) operations.
    def _parse_disjunction(self, tokens: List[str]) -> Node:
        left = self._parse_conjunction(tokens)
        while tokens and tokens[0] == '|':
            tokens.pop(0)
            right = self._parse_conjunction(tokens)
            left = self.Node('|', left, right)
        return left
#Handles logical AND (&) operations.
    def _parse_conjunction(self, tokens: List[str]) -> Node:
        left = self._parse_unary(tokens)
        while tokens and tokens[0] == '&':
            tokens.pop(0)
            right = self._parse_unary(tokens)
            left = self.Node('&', left, right)
        return left
#Handles negations (~) and parenthesis grouping.
    def _parse_unary(self, tokens: List[str]) -> Node:
        if tokens and tokens[0] == '~':
            tokens.pop(0)
            operand = self._parse_unary(tokens)
            return self.Node('~', operand)
        elif tokens and tokens[0] == '(':
            tokens.pop(0)
            expr = self._parse_expression(tokens)
            if not tokens or tokens[0] != ')':
                raise ValueError("Missing closing parenthesis")
            tokens.pop(0)
            return expr
        elif tokens and tokens[0].isupper():
            var = tokens.pop(0)
            return self.Node(var)
        else:
            raise ValueError(f"Unexpected token: {tokens[0] if tokens else 'EOF'}")
#Removes equivalence (<->) and implication (->) by rewriting them using OR and NOT rules.
    def eliminate_equivalence(self, node: Node) -> Node:
        if node is None:
            return None
        if node.value == '<->':
            left_impl = self.Node('->', node.left, node.right)
            right_impl = self.Node('->', node.right, node.left)
            return self.Node('&', self.eliminate_equivalence(left_impl), self.eliminate_equivalence(right_impl))
        elif node.value == '->':
            neg_left = self.Node('~', self.eliminate_equivalence(node.left))
            return self.Node('|', neg_left, self.eliminate_equivalence(node.right))
        elif node.value in ['&', '|']:
            return self.Node(node.value, self.eliminate_equivalence(node.left), self.eliminate_equivalence(node.right))
        elif node.value == '~':
            return self.Node('~', self.eliminate_equivalence(node.left))
        else:
            return node
#Applies De Morgan’s laws and simplifies double negations.
#how negations interact with and & or
    def apply_demorgan(self, node: Node) -> Node:
        if node is None:
            return None
        if node.value == '~':
            if node.left.value == '&':
                return self.Node('|',
                                 self.apply_demorgan(self.Node('~', node.left.left)),
                                 self.apply_demorgan(self.Node('~', node.left.right)))
            elif node.left.value == '|':
                return self.Node('&',
                                 self.apply_demorgan(self.Node('~', node.left.left)),
                                 self.apply_demorgan(self.Node('~', node.left.right)))
            elif node.left.value == '~':
                return self.apply_demorgan(node.left.left)
        elif node.value in ['&', '|']:
            return self.Node(node.value, self.apply_demorgan(node.left), self.apply_demorgan(node.right))
        return node
#Converts formulas to CNF form by distributing ORs over ANDs.
    def distribute_disjunction(self, node: Node) -> Node:
        if node is None:
            return None
        if node.value == '|':
            if node.right and node.right.value == '&':
                left_dist = self.Node('|', node.left, node.right.left)
                right_dist = self.Node('|', node.left, node.right.right)
                return self.Node('&',
                                 self.distribute_disjunction(left_dist),
                                 self.distribute_disjunction(right_dist))
            elif node.left and node.left.value == '&':
                left_dist = self.Node('|', node.left.left, node.right)
                right_dist = self.Node('|', node.left.right, node.right)
                return self.Node('&',
                                 self.distribute_disjunction(left_dist),
                                 self.distribute_disjunction(right_dist))
        if node.value in ['&', '|']:
            return self.Node(node.value, self.distribute_disjunction(node.left), self.distribute_disjunction(node.right))
        return node
#Simplifies CNF by removing duplicate clauses
    def simplify_cnf(self, node: Node) -> Node:
        if node is None:
            return None
        if node.value == '&':
            left_simplified = self.simplify_cnf(node.left)
            right_simplified = self.simplify_cnf(node.right)
            if self._trees_equal(left_simplified, right_simplified):
                return left_simplified
            return self.Node('&', left_simplified, right_simplified)
        elif node.value == '|':
            left_simplified = self.simplify_cnf(node.left)
            right_simplified = self.simplify_cnf(node.right)
            if self._trees_equal(left_simplified, right_simplified):
                return left_simplified
            return self.Node('|', left_simplified, right_simplified)
        return node
#Helper: checks if two syntax trees are structurally identical.
    def _trees_equal(self, tree1: Node, tree2: Node) -> bool:
        if tree1 is None and tree2 is None:
            return True
        if tree1 is None or tree2 is None:
            return False
        if tree1.value != tree2.value:
            return False
        return (self._trees_equal(tree1.left, tree2.left) and self._trees_equal(tree1.right, tree2.right))
#Complete CNF conversion pipeline — combines all above steps and returns clauses
    def cnfConvert(self, formula_str: str) -> List[List[str]]:
        formula_tree = self.parse_formula(formula_str)
        step1 = self.eliminate_equivalence(formula_tree)
        step2 = self.apply_demorgan(step1)
        step3 = self.distribute_disjunction(step2)
        step4 = self.simplify_cnf(step3)
        return self._tree_to_clauses(step4)
#Converts a CNF syntax tree into a list of individual clauses.
    def _tree_to_clauses(self, node: Node) -> List[List[str]]:
        if node is None:
            return []
        if node.value == '&':
            left_clauses = self._tree_to_clauses(node.left)
            right_clauses = self._tree_to_clauses(node.right)
            return left_clauses + right_clauses
        elif node.value == '|':
            literals = self._extract_literals(node)
            return [literals]
        else:
            return [[self._node_to_literal(node)]]
#Collects all literal strings from a disjunction node.
    def _extract_literals(self, node: Node) -> List[str]:
        if node is None:
            return []
        if node.value == '|':
            left_literals = self._extract_literals(node.left)
            right_literals = self._extract_literals(node.right)
            return left_literals + right_literals
        return [self._node_to_literal(node)]
#Converts a single node into a literal string (like 'P' or '~Q').
    def _node_to_literal(self, node: Node) -> str:
        if node.value == '~':
            return f"~{node.left.value}"
        else:
            return node.value


class ResolutionProver:
    #Initializes counters and storage for proof steps.
    def __init__(self):
        self.steps = 0
        self.max_clauses = 0
        self.proof_sequence = []
#Applies resolution iteratively,Detects contradiction (empty clause)
    def plResolution(self, premises: List[str], goal: str, strategy: int = 0,
                     max_steps: int = 1000, max_clauses: int = 10000) -> Tuple[bool, int, int, List[str]]:
        self.steps = 0
        self.max_clauses = 0
        self.proof_sequence = []

        pl = PropositionalLogic()
        clauses = []
        for premise in premises:
            clauses.extend(pl.cnfConvert(premise))

        negated_goal = f"~({goal})"
        goal_clauses = pl.cnfConvert(negated_goal)

        sos = set(self._clause_to_tuple(clause) for clause in goal_clauses)
        other_clauses = set(self._clause_to_tuple(clause) for clause in clauses)
        all_clauses = sos | other_clauses

        self._update_max_clauses(len(all_clauses))

        while sos and self.steps < max_steps and len(all_clauses) < max_clauses:
            sos_clause_tuple = next(iter(sos))
            sos_clause = list(sos_clause_tuple)
            sos.remove(sos_clause_tuple)

            new_clauses = set()
            for other_clause_tuple in all_clauses - {sos_clause_tuple}:
                other_clause = list(other_clause_tuple)
                resolvents = self._resolve_clauses(sos_clause, other_clause)
                for resolvent in resolvents:
                    resolvent_tuple = tuple(sorted(resolvent))
                    if not resolvent:
                        self.steps += 1
                        self.proof_sequence.append(f"Resolved {sos_clause} with {other_clause} -> EMPTY")
                        self._update_max_clauses(len(all_clauses))
                        return True, self.steps, self.max_clauses, self.proof_sequence
                    if resolvent_tuple not in all_clauses and resolvent_tuple not in new_clauses:
                        new_clauses.add(resolvent_tuple)
                        self.proof_sequence.append(f"Resolved {sos_clause} with {other_clause} -> {resolvent}")
            self.steps += 1
            if strategy == 1:
                new_clauses = self._simplify_clauses(new_clauses)
                all_clauses = self._simplify_clauses(all_clauses)
            for new_clause in new_clauses:
                sos.add(new_clause)
                all_clauses.add(new_clause)
            self._update_max_clauses(len(all_clauses))
            if len(all_clauses) >= max_clauses:
                raise MemoryError("Maximum clause limit exceeded")

        if self.steps >= max_steps:
            raise TimeoutError("Maximum step limit exceeded")
        return False, self.steps, self.max_clauses, self.proof_sequence
#Performs the resolution step between two clauses, removing complementary literals.
    def _resolve_clauses(self, clause1: List[str], clause2: List[str]) -> List[List[str]]:
        resolvents = []
        for literal1 in clause1:
            for literal2 in clause2:
                if (literal1.startswith('~') and literal1[1:] == literal2) or \
                   (literal2.startswith('~') and literal2[1:] == literal1):
                    resolvent = [l for l in clause1 if l != literal1] + [l for l in clause2 if l != literal2]
                    resolvent = list(dict.fromkeys(resolvent))
                    if not self._is_valid_clause(resolvent):
                        resolvents.append(resolvent)
        return resolvents
#Checks if a clause is trivially true (contains both a literal and its negation).
    def _is_valid_clause(self, clause: List[str]) -> bool:
        for literal in clause:
            if literal.startswith('~'):
                if literal[1:] in clause:
                    return True
            else:
                if f"~{literal}" in clause:
                    return True
        return False
#Simplifies clauses using absorption and removes valid ones.
    def _simplify_clauses(self, clauses: Set[Tuple[str]]) -> Set[Tuple[str]]:
        simplified = set()
        clause_list = [set(clause) for clause in clauses]
        i = 0
        while i < len(clause_list):
            clause1 = clause_list[i]
            if self._has_complementary_pair(clause1):
                i += 1
                continue
            subsumed = False
            j = 0
            while j < len(clause_list) and not subsumed:
                if i != j:
                    clause2 = clause_list[j]
                    if clause1.issuperset(clause2):
                        subsumed = True
                j += 1
            if not subsumed:
                simplified.add(tuple(sorted(clause1)))
            i += 1
        return simplified
#Detects complementary literals inside a single clause.
    def _has_complementary_pair(self, clause: Set[str]) -> bool:
        for literal in clause:
            if literal.startswith('~'):
                if literal[1:] in clause:
                    return True
            else:
                if f"~{literal}" in clause:
                    return True
        return False
#Converts a list of literals into a tuple for hashing (
    def _clause_to_tuple(self, clause: List[str]) -> Tuple[str]:
        return tuple(sorted(clause))
#Tracks the maximum number of clauses generated during the resolution.
    def _update_max_clauses(self, current_count: int):
        if current_count > self.max_clauses:
            self.max_clauses = current_count


def main():
    print("Propositional Logic Theorem Prover")
    print("Enter premises (one per line, empty line to finish):")
    premises = []
    while True:
        line = input().strip()
        if not line:
            break
        premises.append(line)

    print("Enter goal formula:")
    goal = input().strip()
    print("Select strategy (0 - set-of-support, 1 - set-of-support + simplification):")
    strategy = int(input().strip())
    print("Enter maximum steps (default 1000):")
    try:
        max_steps = int(input().strip())
    except:
        max_steps = 1000
    print("Enter maximum clauses (default 10000):")
    try:
        max_clauses = int(input().strip())
    except:
        max_clauses = 10000

    prover = ResolutionProver()
    try:
        result, steps, max_clauses_used, proof_seq = prover.plResolution(premises, goal, strategy, max_steps, max_clauses)
        print("\n" + "=" * 50)
        if result:
            print("RESULT: Goal is proven")
        else:
            print("RESULT: Goal cannot be proven")
        print(f"Steps: {steps}")
        print(f"Maximum clauses in memory: {max_clauses_used}")
        print("\nProof sequence:")
        for step in proof_seq:
            print(f"  {step}")
    except MemoryError as e:
        print(f"ERROR: {e}")
    except TimeoutError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    print("Testing formula conversion:")
    pl = PropositionalLogic()
    test_formulas = [
        "(P -> Q) & ~R",
        "((P | Q) | ~R) & S",
        "(P & Q) <-> (R | S)"
    ]
    for formula in test_formulas:
        print(f"\nFormula: {formula}")
        try:
            clauses = pl.cnfConvert(formula)
            print(f"Clausal form: {clauses}")
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 50)
    print("Testing theorem proving:")
    prover = ResolutionProver()
    premises1 = ["P -> Q", "P"]
    goal1 = "Q"
    print(f"\nPremises: {premises1}")
    print(f"Goal: {goal1}")
    try:
        result, steps, max_clauses, proof = prover.plResolution(premises1, goal1)
        print(f"Result: {result}, Steps: {steps}, Max clauses: {max_clauses}")
    except Exception as e:
        print(f"Error: {e}")

    premises2 = ["(P -> Q) & (Q -> R)", "P"]
    goal2 = "R"
    print(f"\nPremises: {premises2}")
    print(f"Goal: {goal2}")
    try:
        result, steps, max_clauses, proof = prover.plResolution(premises2, goal2)
        print(f"Result: {result}, Steps: {steps}, Max clauses: {max_clauses}")
    except Exception as e:
        print(f"Error: {e}")

    # main()

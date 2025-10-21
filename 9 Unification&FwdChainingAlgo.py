# ================================================================
# AI LAB TASK - EXERCISE 9.19
# Implementing Unification Algorithm + Forward Chaining Algorithm
# ================================================================


# computes Cartesian products
from itertools import product

# ----------------------------------
# Unification algorithm


#theta — a dictionary (a list of variable replacements we already know).
def unify(x, y, theta=None):
    #If no substitution list was given, start with an empty one.
    if theta is None:
        theta = {}
#If both things are exactly the same, then just return what we already have.
    if x == y:
        return theta
    
#lowercase = variable, uppercase/other = constant or functor name
#A functor is the name of a function or relation symbol in logic expressions.It’s basically the main operator or predicate name.

#instance-It’s a built-in Python function that checks the type of a variable.
#isinstance(object, type)
#It returns:
#True — if the object is of that given type
#False — otherwise
    if isinstance(x, str) and x.islower():  # variable
        return unify_var(x, y, theta)
    elif isinstance(y, str) and y.islower():  # variable
        return unify_var(y, x, theta)
    #"Father", "John") → means Father(John)   
    # tuples represent predicates or functions with arguments.
    #If both sides are structured expressions of the same shape (same number of arguments),then try to unify them element by element
    elif isinstance(x, tuple) and isinstance(y, tuple) and len(x) == len(y):
        #unify the corresponding components pairwise.
        #The built-in zip() pairs up each element from both tuples.
        #x = ("Ancestor", "x", "y")
#y = ("Ancestor", "John", "Mary")
#then zip(x, y) gives pairs:
#("Ancestor", "Ancestor")
#("x", "John")
#("y", "Mary")
        for a, b in zip(x, y):
          #We recursively call unify() for each corresponding pair (a, b).
          #unify("x", "John", {}) → {'x': 'John'}
#unify("y", "Mary", {'x': 'John'}) → {'x': 'John', 'y': 'Mary'}

            theta = unify(a, b, theta)
            #If at any point, one of the pairs cannot be unified (for example ("Father", "Mother")then unify() returns None → meaning failure
            if theta is None:
                return None
            #If all pairs were unified successfully, we return the final theta dictionary which contains all the variable bindings found.
        return theta
    
    # x == y → directly equal → success
    # Either x or y is a variable → handle with unify_var()
    # Both are tuples of same length → unify element by element
    # Now, if none of those conditions are true, it means:
    # he two things cannot be unified at all.
    else:
        return None

#decides how a variable should be bound during unification.
def unify_var(var, x, theta):
    #“If this variable (var) already has a value assigned in the substitution dictionary theta,then try to unify that value with x again
    if var in theta:
        return unify(theta[var], x, theta)
    
    #This is the “infinite loop guard.”It checks if the variable var appears inside the expression x.If yes → unification is not allowed (would cause circular binding).
    #unify_var('x', ('Father', 'x'), {})Here we’re trying to make x = Father(x) That’s impossible — x would depend on itself forever.
    elif occurs_check(var, x, theta):
        return None
    else:
        theta[var] = x
        return theta

#Does the variable var occur inside the expression x
#If yes → it would cause an infinite loop, so return True.
#If not → return False
def occurs_check(var, x, theta):
    #occurs_check('x', 'x', {})Yes, 'x' occurs inside itself → return True 
    if var == x:
        return True
    elif isinstance(x, tuple):
        return any(occurs_check(var, xi, theta) for xi in x)
    #ensures that chains of variable bindings are also checked.handles indirect references via the substitution dictionary theta
    elif isinstance(x, str) and x in theta:
        return occurs_check(var, theta[x], theta)
    return False


# ------------------------------------------------------------
# Forward Chaining algorithm for first-order Horn clauses

def forward_chain_first_order(KB, query, max_iterations=15):
    terms = set(["John"])  # known constantsymbols
    facts = set()#storing all the facts inferred so far
    iteration = 0#to avoid  infinite loops

#(The pretty() function just formats logical expressions in readable form, like turning ("Ancestor", "x", "y") → Ancestor(x, y).)
    print(f"Initial known terms: {list(terms)}")
    #What the target query is (like Ancestor(Mother(y), John)).
    print(f"Query: {pretty(query)}")
    print("-------------------------------------------------------------------------")

    while iteration < max_iterations:
        iteration += 1
        #o collect newly inferred facts.
        new_facts = set()
        #every loop we print the facts known so far.
        print(f"\n--- Iteration {iteration} ---")
        if facts:
            print("Known ground facts:")
            for f in facts:
                print(f"   {pretty(f)}")
        else:
            print("Known ground facts:\n  (none yet)")

        # Apply rules
        for rule in KB:
            #Rules (that have an implication =>)   Simple facts (without =>)
            if "=>" not in rule:
                continue
             #skips facts and processes only rules.
             #lhs premise
             #rhs conclusion
             #varsinrule   are the variables.
            lhs, rhs = rule["=>"]
            vars_in_rule = list(collect_vars(lhs) | collect_vars(rhs))
            #trying to assign all values in subs . like if we have J,M then possibilities become, JM MJ JJ MM 
            for assignment in product(list(terms), repeat=len(vars_in_rule)):
                subs = dict(zip(vars_in_rule, assignment))
                #substitte/replace and test the rule.
                lhs_inst = substitute(lhs, subs)
                rhs_inst = substitute(rhs, subs)
                #If all premises unify/matches with known facts → rule is applicable 
                if all(any(unify(prem, f, {}) is not None for f in facts) for prem in lhs_inst):
                    #add a new inferred fact that is conclusion, also add if any new teerms appeared
                    new_fact = make_hashable(rhs_inst[0])
                    if new_fact not in facts:
                        new_facts.add(new_fact)
                        terms |= collect_terms(new_fact)

        # Base fact: Ancestor(Mother(x), x)
        #This adds the special base rule Everyone’s mother is their ancestor.
        base_fact = ("Ancestor", ("Mother", "x"), "x")
        for t in list(terms):  # ✅ iterate over a copy to avoid set modification
            inst_fact = substitute(base_fact, {"x": t})[0]
            inst_fact = make_hashable(inst_fact)
            if inst_fact not in facts:
                new_facts.add(inst_fact)
                terms |= collect_terms(inst_fact)
       #stop if nthing new inferred.query cant be proved.
        if not new_facts:
              print("\nNo new facts inferred — stopping.")
    # Format facts neatly using pretty()
              pretty_facts = [pretty(f) for f in facts]
              print("Facts = { " + ", ".join(pretty_facts) + " }")
              print(f"Terms = {{ {', '.join(sorted(terms))} }}")
              print("Result: NO ❌\n")
              return False




        print("\nNew facts added this iteration:")
        for f in new_facts:
            print(f"   {pretty(f)}")
      #After generating new facts:Print them nicely.Try to unify each new fact with the query (goal).If any unify → the query is proven ✅ → return True.
        for f in new_facts:
           theta = unify(f, query, {})
           if theta is not None:
            print(f"\nFacts = {{ {', '.join(pretty(fa) for fa in facts | new_facts)} }}")
            print(f"Terms = {{ {', '.join(sorted(terms))} }}")
            print(f"\n✅ Query satisfied by fact: {pretty(f)}")

        # Format substitution nicely
            sub_str = ", ".join(f"{v}: {k}" for v, k in theta.items())
            print(f"   substitution: {{ {sub_str} }}")
            print("Result: YES ✅\n")
            return True


       #merge new facts and continue.
        facts |= new_facts
#If loop ran max_iterations times and didn’t stop earlier →we assume we didn’t reach a conclusion → output UNKNOWN.
    print("\nMax iterations reached — stopping.")
    print("Result: UNKNOWN \n")
    return False

# ------------------------------------------------------------
#  Helper functions
#This function replaces all variables in a predicate (or rule)with their actual assigned values from a substitution dictionary (subs)
def substitute(predicate, subs):
    #Case 1 — Nested tuple (special 3-argument form)
    #predicate = ("Ancestor", ("Mother", "x"), "x")subs = {"x": "John"}
    #[("Ancestor", ("Mother", "John"), "John")]
    if isinstance(predicate, tuple) and len(predicate) == 3 and isinstance(predicate[1], tuple):
        return [(predicate[0], substitute(predicate[1], subs), substitute(predicate[2], subs))]
    #Simple tuple (no nested functor) ("Ancestor", "x", "y")
    elif isinstance(predicate, tuple):
        return [tuple(substitute(arg, subs) if isinstance(arg, tuple) else subs.get(arg, arg) for arg in predicate)]
   #Case 3 — List of predicates (like LHS or RHS of rule)aply substitution to each one.
   #predicate = [("Ancestor", "x", "y"), ("Ancestor", "y", "z")]
    #subs = {"x": "John", "y": "Mary", "z": "Sam"}→ output:
#[
#  [("Ancestor", "John", "Mary")],
#  [("Ancestor", "Mary", "Sam")]
#]
    elif isinstance(predicate, list):
        return [substitute(p, subs) for p in predicate]
    #Case 4 — Simple variable or constant
    # If it’s just a single symbol, like "x" or "John",replace it if it’s in the substitution dictionary.Otherwise, leave it as is.
    else:
        return subs.get(predicate, predicate)

#unify() = “Find how to make them match.”substitute() = “Apply that match.”



def collect_vars(expr):
    #If the expression is a string and all letters are lowercase (like "x", "y", "z"),s
    # then it’s a variable — so we return it as a one-element set
    if isinstance(expr, str) and expr.islower():
        return {expr}
    #Case 2 — Expression is a tuple (like ("Ancestor", "x", "y")),(predicate or function)
    elif isinstance(expr, tuple):
        s = set()
        for e in expr:
            s |= collect_vars(e)
        return s
    #Case 3 — Expression is a list (set of predicates)
    #expr = [
    #("Ancestor", "x", "y"),
    #("Ancestor", "y", "z")
#collect_vars(expr) ➜ {"x", "y", "z"}
    elif isinstance(expr, list):
        s = set()
        for e in expr:
            s |= collect_vars(e)
        return s
    return set()

#collect_terms() finds all constants / object names (like John, Mary, etc.).
def collect_terms(expr):
    #case1 -constant string
    # If expr is a string and not lowercase,then it’s a constant name, so we collect it.
    if isinstance(expr, str) and not expr.islower():
        return {expr}
    #Case 2 — Tuple (predicate or functor) expr = ("Ancestor", "John", "x") 
    # Returns {"Ancestor", "John"}
    elif isinstance(expr, tuple):
        s = set()
        for e in expr:
            s |= collect_terms(e)
        return s
    #Case 3 — List (list of predicates) expr = [("Ancestor", "John", "x"), ("Parent", "x", "Mary")]
#collect_terms(expr) Returns {"Ancestor", "Parent", "John", "Mary"}
    elif isinstance(expr, list):
        s = set()
        for e in expr:
            s |= collect_terms(e)
        return s
    return set()




#| Input                                | Output                               | Explanation                  |
#| ------------------------------------ | ------------------------------------ | ---------------------------- |
#| `["A", "B", "C"]`                    | `("A", "B", "C")`                    | List → tuple                 |
#| `[("Parent", "John", "x")]`          | `(("Parent", "John", "x"),)`         | Nested list → tuple of tuple |
#| `("Ancestor", ["Mother", "y"], "x")` | `("Ancestor", ("Mother", "y"), "x")` | Inner list converted         |
#| `"John"`                             | `"John"`                             | Already hashable             |

def make_hashable(x):
    #List → tuple
    if isinstance(x, list):
        return tuple(make_hashable(i) for i in x)
    #Nested list → tuple of tuple
    elif isinstance(x, tuple):
        return tuple(make_hashable(i) for i in x)
    #Inner list converted / Already hashable
    return x

#printing facts and queries in a clean, human-readable format.
def pretty(expr):
    #Check if the expression is a tuple   
    #("Ancestor", "x", "y")  →  Ancestor(x, y)

    if isinstance(expr, tuple):
        functor = expr[0]
        args = expr[1:]

        #If there are no arguments  Then just return the functor itself.
        if not args:
            return str(functor)
        #If arguments themselves contain tuples,("Ancestor", ("Mother", "y"), "John")),
#then we recursively call pretty() again for each argument.
        # Recursively pretty-print each argument
        pretty_args = []
        for a in args:
            pretty_args.append(pretty(a))
        return f"{functor}({', '.join(pretty_args)})"
    #Base case:  If the input isn’t a tuple (e.g., just "x" or "John"),then convert it to string directly.
    else:
        return str(expr)



# ------------------------------------------------------------
# Knowledge Base (KB)
KB = [
    {"=>": ([("Ancestor", "x", "y"), ("Ancestor", "y", "z")],
             [("Ancestor", "x", "z")])},

    {"=>": ([], [("Ancestor", ("Mother", "x"), "x")])}         
]

# ------------------------------------------------------------
#  Queries from Exercise 9.19
queries = [
    ("Ancestor", ("Mother", "y"), "John"),
    ("Ancestor", ("Mother", ("Mother", "y")), "John"),
    ("Ancestor", ("Mother", ("Mother", ("Mother", "y"))), ("Mother", "y")),
    ("Ancestor", ("Mother", "John"), ("Mother", ("Mother", "John")))
]

# ------------------------------------------------------------
# Run all queries
for i, q in enumerate(queries, start=1):
    print("====================")
    print(f"Query ({i}): {pretty(q)}")
    result = forward_chain_first_order(KB, q)     

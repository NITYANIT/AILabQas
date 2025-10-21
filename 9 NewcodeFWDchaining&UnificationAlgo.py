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
        for a, b in zip(x, y):
            theta = unify(a, b, theta)
            if theta is None:
                return None
        return theta
    else:
        return None

#decides how a variable should be bound during unification.
def unify_var(var, x, theta):
    if var in theta:
        return unify(theta[var], x, theta)
    elif occurs_check(var, x, theta):
        return None
    else:
        theta[var] = x
        return theta

def occurs_check(var, x, theta):
    if var == x:
        return True
    elif isinstance(x, tuple):
        return any(occurs_check(var, xi, theta) for xi in x)
    elif isinstance(x, str) and x in theta:
        return occurs_check(var, theta[x], theta)
    return False

# ------------------------------------------------------------
# Forward Chaining algorithm for first-order Horn clauses

def forward_chain_first_order(KB, query, max_iterations=15):
    terms = set(["John"])  # known constantsymbols
    facts = set()#storing all the facts inferred so far
    iteration = 0#to avoid  infinite loops

    print(f"Initial known terms: {list(terms)}")
    print(f"Query: {pretty(query)}")
    print("-------------------------------------------------------------------------")

    while iteration < max_iterations:
        iteration += 1
        new_facts = set()
        print(f"\n--- Iteration {iteration} ---")
        if facts:
            print("Known ground facts:")
            for f in facts:
                print(f"   {pretty(f)}")
        else:
            print("Known ground facts:\n  (none yet)")

        # Apply rules
        for rule in KB:
            ## If the rule doesn’t have an implication (=>), skip it
            # Example of a rule with => : { "=>": ([premises], [conclusion]) }
            if "=>" not in rule:
                continue
            lhs, rhs = rule["=>"]
            vars_in_rule = list(collect_vars(lhs) | collect_vars(rhs))
            #try every combination now
            for assignment in product(list(terms), repeat=len(vars_in_rule)):
                subs = dict(zip(vars_in_rule, assignment))
                lhs_inst = substitute(lhs, subs)
                rhs_inst = substitute(rhs, subs)
                # Check if all premises in LHS are already true (in known facts)
        #   - For each premise, see if it unifies with any known fact
                if all(any(unify(prem, f, {}) is not None for f in facts) for prem in lhs_inst):
                    new_fact = make_hashable(rhs_inst[0])
                    if new_fact not in facts:
                        new_facts.add(new_fact)
                        terms |= collect_terms(new_fact)

        #stop if nothing new inferred.query cant be proved.
        if not new_facts:
             print("\nNo new facts inferred — stopping.")
             print(f"Facts = {{ {', '.join(pretty(fa) for fa in facts)}  }}")
             print(f"Terms = {{ {', '.join(sorted(terms))} }}")
             print("Result: NO ❌\n")
             return False
    
        print("\nNew facts added this iteration:")
        for f in new_facts:
            print(f"   {pretty(f)}")

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
                return True  # ✅ must align with the 'if' (4 spaces more than for)

        # ✅ this must be OUTSIDE the for-loop but INSIDE the while-loop
        facts |= new_facts


    print("\nMax iterations reached — stopping.")
    print("Result: UNKNOWN \n")
    return False

# ------------------------------------------------------------
#  Helper functions

def substitute(predicate, subs):
    # ✅ FIXED VERSION (keeps output consistent and hashable)
    if isinstance(predicate, tuple):
        return tuple(substitute(arg, subs) if isinstance(arg, tuple) else subs.get(arg, arg) for arg in predicate)
    elif isinstance(predicate, list):
        return [substitute(p, subs) for p in predicate]
    else:
        return subs.get(predicate, predicate)

def collect_vars(expr):
    if isinstance(expr, str) and expr.islower():
        return {expr}
    elif isinstance(expr, tuple):
        s = set()
        for e in expr:
            s |= collect_vars(e)
        return s
    elif isinstance(expr, list):
        s = set()
        for e in expr:
            s |= collect_vars(e)
        return s
    return set()

def collect_terms(expr):
    if isinstance(expr, str) and not expr.islower():
        return {expr}
    elif isinstance(expr, tuple):
        s = set()
        for e in expr:
            s |= collect_terms(e)
        return s
    elif isinstance(expr, list):
        s = set()
        for e in expr:
            s |= collect_terms(e)
        return s
    return set()

def make_hashable(x):
    ## If x is a list, convert each element into a hashable form (recursively)
    # and then make it a tuple.
    if isinstance(x, list):
        return tuple(make_hashable(i) for i in x)
    ## If x is a tuple, check if it contains lists inside — and convert them too.
    elif isinstance(x, tuple):
        return tuple(make_hashable(i) for i in x)
    ## Otherwise (string, number, etc.) — already hashable, so return it as is.
    return x

def pretty(expr):
    if isinstance(expr, tuple):
        functor = expr[0]
        args = expr[1:]
        if not args:
            return str(functor)
        pretty_args = [pretty(a) for a in args]
        return f"{functor}({', '.join(pretty_args)})"
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
#“Go through every query in the list called queries,and while doing so, also give me a counter i starting from 1
for i, q in enumerate(queries, start=1):
    print("====================")
    print(f"Query ({i}): {pretty(q)}")
    result = forward_chain_first_order(KB, q)

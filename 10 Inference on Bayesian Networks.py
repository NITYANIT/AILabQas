#to perform infreence on bn and verify conditional independence.
import itertools #for looping for generating t/f combiations

# the Bayesian Network using a dictionary
bn = {
    "Burglary": {
        "parents": [],
        "cpt": {True: 0.001, False: 0.999}
    },
    "Earthquake": {
        "parents": [],
        "cpt": {True: 0.002, False: 0.998}
    },
    "Alarm": {
        "parents": ["Burglary", "Earthquake"],
        "cpt": {
            (True, True): 0.95,
            (True, False): 0.94,
            (False, True): 0.29,
            (False, False): 0.001
        }
    },
    "JohnCalls": {
        "parents": ["Alarm"],
        "cpt": {True: 0.90, False: 0.05}
    },
    "MaryCalls": {
        "parents": ["Alarm"],
        "cpt": {True: 0.70, False: 0.01}
    }
}

# Helper function: probability of a variable given evidence
#Get the parents and CPT of the variable.
def P(var, value, evidence, bn):
    parents = bn[var]["parents"]
    cpt = bn[var]["cpt"]
    if not parents:  # root node:if no parents directly return its prior prob
        return cpt[value]
    #if parents ,truth values ina tuple  → key = (True, False)
    #create a tuple of parents
    key = tuple(evidence[p] for p in parents)
    if len(key) == 1:  
        key = key[0] # from (True,) → True
    #If we ask for P(Alarm=True | Burglary, Earthquake), return that.
    # If we ask for P(Alarm=False | ...), return 1 minus that.
    p_true = cpt[key]
    return p_true if value else 1 - p_true


# Recursive enumeration over all hidden variables
#t sums over all values of the hidden variables to compute the total prob of your query.
def enumerate_all(vars_list, evidence, bn):
    #If there are no more variables left to process, we return 1.
    if not vars_list:
        return 1.0
    #vars_list = ['Burglary', 'Earthquake', 'Alarm', 'JohnCalls', 'MaryCalls']
    # Y = 'Burglary'
    # rest = ['Earthquake', 'Alarm', 'JohnCalls', 'MaryCalls']
    Y = vars_list[0]#first var
    rest = vars_list[1:]#remaining list of vars
#We check if we already know the value of Y from the evidence.
#if evidence = { 'Burglary': True }, then when Y = 'Burglary' → known
    if Y in evidence:
        #we don’t need to sum over its possible values as we alreday know
        #builds up the total joint probability:p(x1,x2,x3)=p(x1|parents)*p(x2,x3|x1)
        #P(Alarm=True) × P(JohnCalls, MaryCalls | Alarm=True)
        return P(Y, evidence[Y], evidence, bn) * enumerate_all(rest, evidence, bn)
    else:
        total = 0
        #marginalisatin
        for y in [True, False]:
            total += P(Y, y, evidence, bn) * enumerate_all(rest, {**evidence, Y: y}, bn)
        return total


# Query function for any variable
def query(X, evidence, bn):
    dist = {}#dist will store the unnormalized probabilities of X=True and X=False.
    vars_list = list(bn.keys())

    for x in [True, False]:
        #{**evidence, X: x} means:
        # take the current evidence
        # add/overwrite X with its value (True or False).
        # Then we call enumerate_all(...) to compute the total joint probability of everything consistent with that case.
        dist[x] = enumerate_all(vars_list, {**evidence, X: x}, bn)

    # Normalize
    total = dist[True] + dist[False]
    for k in dist:
        #we convert from joint probabilities to conditional probabilities:
        dist[k] = round(dist[k] / total, 4) 
    return dist



# (a) 
print("P(JohnCalls | Burglary, Earthquake) =",
      query("JohnCalls", {"Burglary": True, "Earthquake": True}, bn)[True])

# (b) 
print("P(Alarm | Burglary) =",
      query("Alarm", {"Burglary": True}, bn)[True])

# (c)
print("P(Earthquake | MaryCalls) =",
      query("Earthquake", {"MaryCalls": True}, bn)[True])

# (d)
print("P(Burglary | Alarm) =",
      query("Burglary", {"Alarm": True}, bn)[True])

# Compute joint P(JohnCalls, MaryCalls | Alarm)
p_joint = query("JohnCalls", {"MaryCalls": True, "Alarm": True}, bn)[True]

# Compute individual P(JohnCalls | Alarm)
p_indep = query("JohnCalls", {"Alarm": True}, bn)[True]

print("P(JohnCalls and MaryCalls | Alarm) =", p_joint)
print("P(JohnCalls | Alarm) =", p_indep)

#Once we know whether the alarm rang, does Mary calling tell us anything new about whether John calls?
if abs(p_joint - p_indep) < 1e-3: #are equal almost
    print("JohnCalls and MaryCalls are conditionally independent given Alarm.")
else:
    print("They are NOT independent.")

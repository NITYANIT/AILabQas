import random#Python's pseudo-random generator
from collections import defaultdict#like a normal dictionary, but it automatically provides default values for new keys — avoiding KeyErrors.

class BayesianNetworkInference:
    def __init__(self, bn):
        self.bn = bn
        self.variables = list(bn.keys())#ensure bn was defined in topological order.

    # --- Helper: sample from Bernoulli(p)
    def sample_boolean(self, prob):
        #random.random()-This function returns a random floating-point number between 0.0 and 1.0.
        #prob-This is the probability of an event being True
        return random.random() < prob

    # --- Helper: get P(X=True | parents)
    #reads the correct probability from the CPT based on the current evidence.
    def get_prob(self, var, evidence):
        node = self.bn[var]
        #It builds a tuple of parent values in the same order listed in node['parents'] and reads the CPT.
        parents = node['parents']
        parent_vals = tuple(evidence[p] for p in parents)
        #evidence (or partial sample) must already contain values for all parents; otherwise KeyError.
        return node['cpt'][parent_vals]

    # PRIOR SAMPLING
    #N: number of samples to generate
    #query: the variable we want to estimate probability for
    #The goal is to estimate P(query=True) and P(query=False) from simulated samples
    #so we generate random samples,diff cases,let us know at depends on our var , and change accordingly in a random way,which is joint prob .
    def prior_sampling(self, N, query):
        #Will store counts like: True: number_of_times_query_was_True, False: number_of_times_query_was_False}
        counts = defaultdict(int)
        for _ in range(N):
            sample = {}#sample will hold the truth values (True/False) of all variables for one full sample.
           #The list self.variables must be in topological order (parents before children), or else get_prob will fail because parent values won’t be available yet.
            for var in self.variables:
                #Looks up the CPT entry for that variable based on the already-sampled parent values.get_prob('Alarm', sample) → bn['Alarm']['cpt'][(True, False)] = 0.94.
                prob = self.get_prob(var, sample)
                #Performs a Bernoulli trial: returns True with probability prob, else False
                sample[var] = self.sample_boolean(prob)
            counts[sample[query]] += 1
            #Normalize to get probabilities
        total = sum(counts.values())
        #Converts counts to probabilities:{True: count(True)/N, False: count(False)/N}
        return {k: v / total for k, v in counts.items()}

#We now want P(query | evidence) → posterior probability (after observing something).So, we can’t just use prior sampling — we must condition on evidence.But instead of directly conditioning during sampling,we’ll generate all samples like before, and then reject the ones that don’t match the evidence.That’s why it’s called rejection sampling.

    #  REJECTION SAMPLING
    def rejection_sampling(self, N, query, evidence):
        counts = defaultdict(int)
        for _ in range(N):
            sample = {}
            for var in self.variables:
                prob = self.get_prob(var, sample)
                sample[var] = self.sample_boolean(prob)

            # reject inconsistent samples
            if all(sample[e] == evidence[e] for e in evidence):
                counts[sample[query]] += 1

        total = sum(counts.values())
        if total == 0:
            return None
        return {k: v / total for k, v in counts.items()}

#Compute P(query | evidence) again — but avoid wasting samples like rejection sampling does.
# In rejection sampling, most samples are thrown away because they don’t match the evidence → inefficient In likelihood weighting, we force the evidence variables to stay fixed and weigh each sample by how likely that evidence was.

    # LIKELIHOOD WEIGHTING
    def likelihood_weighting(self, N, query, evidence):
        weighted_counts = defaultdict(float)
        for _ in range(N):
            weight = 1.0
            sample = {}
            for var in self.variables:
                prob = self.get_prob(var, sample)
                #If this variable is part of the evidence,we don’t sample it (we already know its value).
                #But — we adjust the weight of this sample based on how likely that evidence was:
                if var in evidence:
                    sample[var] = evidence[var]
                    #If the evidence says var=True, multiply weight by P(var=True | parents) If it says var=False, multiply weight by P(var=False | parents)
                    weight *= prob if evidence[var] else (1 - prob)
                else:
                    sample[var] = self.sample_boolean(prob)
            weighted_counts[sample[query]] += weight
        total = sum(weighted_counts.values())
        return {k: v / total for k, v in weighted_counts.items()}



    # GIBBS SAMPLING-This is a Markov Chain Monte Carlo (MCMC) method — more efficient for networks with many variables.
    #→ using sampling, but instead of generating full samples from scratch each time,we iteratively update one variable at a time — keeping evidence fixed.This creates a “chain” of samples that eventually reflects the true posterior distribution.
    def gibbs_sampling(self, N, query, evidence):
        non_evidence = [v for v in self.variables if v not in evidence]
        state = dict(evidence)
        # random initialization
        for var in non_evidence:
            state[var] = random.choice([True, False])

        counts = defaultdict(int)
        for _ in range(N):
            for var in non_evidence:
                prob_true = self.markov_blanket_prob(var, state)
                state[var] = self.sample_boolean(prob_true)
            counts[state[query]] += 1
#For each iteration:
#Go through each non-evidence variable.
# Compute the probability that this variable should be True given everything else (its Markov Blanket).
# Sample a new value for it (True/False) using that probability.
# Move on to the next variable.
        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()}


    # --- Helpers for Gibbs
    def markov_blanket_prob(self, var, state):
        #It asks: “What’s the probability this variable is True vs False given current state?
        p_true = self.local_prob(var, True, state)
        p_false = self.local_prob(var, False, state)
        return p_true / (p_true + p_false)

#Computes joint probability of var=value with its children given the current state
    def local_prob(self, var, value, state):
        #Make a copy of the current world (state) and temporarily assume that variable has the new value (True or False).
        temp = state.copy()
        temp[var] = value
        p = self.get_prob(var, temp)
        p = p if value else (1 - p)
        # multiply over children
        for child, node in self.bn.items():
            if var in node['parents']:
                prob = self.get_prob(child, temp)
                p *= prob if temp[child] else (1 - prob)
        return p


# ----------------------------
# Example: ALARM NETWORK
# ----------------------------
bn = {
    'Burglary': {'parents': [], 'cpt': {(): 0.001}},
    'Earthquake': {'parents': [], 'cpt': {(): 0.002}},
    'Alarm': {
        'parents': ['Burglary', 'Earthquake'],
        'cpt': {
            (True, True): 0.95,
            (True, False): 0.94,
            (False, True): 0.29,
            (False, False): 0.001
        }
    },
    'JohnCalls': {'parents': ['Alarm'], 'cpt': {(True,): 0.90, (False,): 0.05}},
    'MaryCalls': {'parents': ['Alarm'], 'cpt': {(True,): 0.70, (False,): 0.01}}
}

# Create object
bn_inf = BayesianNetworkInference(bn)

# ----------------------------
# Run different sampling methods
# ----------------------------
print("🔹 Prior Sampling P(Alarm):")
print(bn_inf.prior_sampling(10000, 'Alarm'))

print("\n🔹 Rejection Sampling P(Alarm | JohnCalls=True):")
print(bn_inf.rejection_sampling(10000, 'Alarm', {'JohnCalls': True}))

print("\n🔹 Likelihood Weighting P(Alarm | JohnCalls=True):")
print(bn_inf.likelihood_weighting(10000, 'Alarm', {'JohnCalls': True}))

print("\n🔹 Gibbs Sampling P(Alarm | JohnCalls=True, MaryCalls=True):")
print(bn_inf.gibbs_sampling(5000, 'Alarm', {'JohnCalls': True, 'MaryCalls': True}))

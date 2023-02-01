import copy, math, time
import numpy as np
from tqdm import tqdm

# parent node class
class Node:   
    def getSize(self):
        return self.size
    
    def toString(self):
        raise Exception('Unimplemented method: toString')
    
    def interpret(self):
        raise Exception('Unimplemented method: interpret')

# string node
class Str(Node):
    def __init__(self, value):
        self.value = value  
        
    def toString(self):
        if self.value == '':
            return 'BLANK'
        else:
            return self.value
    
    def interpret(self, env):
        return self.value

# variable node
class Var(Node):
    def __init__(self, name):
        self.value = name
        
    def toString(self):
        return self.value
    
    def interpret(self, env):
        return copy.deepcopy(env[self.value])

# concatenation node
class Concat(Node):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def toString(self):
        return 'concat(' + self.x.toString() + ", " + self.y.toString() + ")"
    
    def interpret(self, env):
        return self.x.interpret(env) + self.y.interpret(env) 

# replace node
class Replace(Node):
    def __init__(self, input_str, old, new):
        self.str = input_str
        self.old = old
        self.new = new
        
    def toString(self):
        return self.str.toString() + '.replace(' + self.old.toString() + ", " + self.new.toString() + ")"
    
    def interpret(self, env):
        return self.str.interpret(env).replace(self.old.interpret(env), self.new.interpret(env), 1)


# guided bottom-up search
class GBUS:
    '''
    Guided bottom-up search class.
    '''
    def __init__(self, grammar, in_out, bound, pcfg_start='equal', update_pcfg=True):
        '''

        Parameters
        ----------
        grammar : dict of the CFG
            all the rules in the CFG
        in_out : list of dicts
            input-output pairs we are looking to solve
        bound : integer
            maximum program cost to check
        pcfg_start : string (either 'equal' or 'final')
            how to start the probabilistic CFG
        update_pcfg : boolean
            whether to update the PCFG

        Returns
        -------
        prog : a sequence of 'Node' classes making up a program
            the program successfully solving all input-output pairs
        
        '''
        # ensure pcfg_start given is correct
        assert pcfg_start in ['equal', 'final']
        # grammar selfs
        self.grammar = grammar
        # other selfs
        self.in_out = in_out
        self.bound = bound
        self.pcfg_start = pcfg_start
        self.update_pcfg = update_pcfg
    
    def true_init(self):
        # initial grammar costs
        if self.update_pcfg == True:
            pcfg_probs = np.ones(len(self.grammar)) / len(self.grammar)
            self.solved_subsets = set()
            self.solved_subsets.add( (0,) * len(in_out) )
        elif self.update_pcfg == False:
            if self.pcfg_start == 'equal':
                pcfg_probs = np.ones(len(self.grammar)) / len(self.grammar)
            elif self.pcfg_start == 'final':
                pcfg_probs = np.array([0.188] * 5 + [0.059])
        
        self.grammar_costs = {}
        for i,rule_str in enumerate(self.grammar.keys()):
            self.grammar_costs[rule_str] = round(-math.log2(pcfg_probs[i]))
        # correct tuple solution
        self.correct_tuple = tuple()
        for io in self.in_out:
            self.correct_tuple += (io['out'],)
        # list of partial solutions
        self.partial_solutions = []
        # total programs evaluated
        self.total_progs_eval = 0
    
    # main search loop
    def run_search(self):
        self.true_init()
        soln = False
        # soln will be None if bound is reached
        while soln is not None:
            prog, soln = self.guided_search()
            # if a solution is found solving all input-output pairs
            if soln == True:
                return prog
            # update the PCFG probabilities and costs
            elif soln == False and self.update_pcfg == True:
                print('updating grammar costs')
                self.update_grammar_costs()
    
    # evaluate a program
    def evaluate_program(self, p, update_plist=True):
        '''

        Parameters
        ----------
        p : a sequence of 'Node' classes making up a program
            program to evaluate.
        update_plist : boolean, optional
            whether the program list should be updated. The default is True.

        Returns
        -------
        program OR None
            program if input-output pairs are solved or PCFG should be updated.
            None otherwise
        bool
            Whether all input-output pairs were solved by the program.

        '''
        # program outputs for equivalence checking
        out_tuple = tuple()
        # which subset of the input-output pairs this program solves
        solved_subset_tuple = tuple()
        # check if outputs are solved correctly
        for idx, io in enumerate(self.in_out):
            out_tuple += (p.interpret(io),)
            if self.update_pcfg == True:
                # 1 if solved, 0 if not solved
                if out_tuple[idx] == self.correct_tuple[idx]:
                    solved_subset_tuple += (1,)
                else:
                    solved_subset_tuple += (0,)
        if out_tuple == self.correct_tuple:
            return (p, True)
        if self.update_pcfg == True:
            # check if solved subset is new
            if solved_subset_tuple not in self.solved_subsets:
                print(solved_subset_tuple)
                print(p.toString())
                self.solved_subsets.add(solved_subset_tuple)
                self.partial_solutions.append((p, solved_subset_tuple))
                return (p, False)
        # check if outputs are not equivalent to any seen before
        if out_tuple not in self.output:
            self.total_progs_eval += 1
            self.output.add(out_tuple)
            if update_plist == True:
                self.plist[self.current_cost].append(p)
        return (None, False)
    
    def guided_search(self):
        '''
        
        Returns
        -------
        program OR None
            program if input-output pairs are solved or PCFG should be updated.
            None otherwise, or if bound is exceeded.
        boolean OR None
            whether all input-output pairs were solved by the program.
            None if bound is exceeded.

        '''
        # initial program list
        self.plist = {}
        
        # costs of initial programs in program list
        init_plist_cost = [self.grammar_costs[key] for key,value in list(self.grammar.items())[:4]]
        
        for cost in set(init_plist_cost):
            self.plist[cost] = []
        for key,value in list(self.grammar.items())[:4]:
            self.plist[self.grammar_costs[key]].append(value)
        
        # next loop cost
        self.current_cost = min(self.plist.keys())
        
        # outputs
        self.output = set()
        # loop over all programs in program list
        for key in self.plist.keys():
            for p in self.plist[key]:
                (prog, soln) = self.evaluate_program(p, update_plist=False)
                if prog is not None:
                    return (prog, soln)
        
        while self.current_cost <= self.bound:
            # iterate over all combinations of sizes to find next smallest size
            newsize_set = set()
            for i in self.plist.keys():
                for j in self.plist.keys():
                    newsize_set.add(i + j + self.grammar_costs['concat'])
                    for k in self.plist.keys():
                        newsize_set.add(i + j + k + self.grammar_costs['replace'])
            newsize_array = np.array(list(newsize_set))
            self.old_cost = self.current_cost
            self.current_cost = np.min(newsize_array[newsize_array > self.old_cost])
            print(self.current_cost)
            # iterate over new programs
            self.plist[self.current_cost] = []
            for p in self.new_programs():
                (prog, soln) = self.evaluate_program(p)
                if prog is not None:
                    return (prog, soln)
        
        return (None, None)

    def new_programs(self):      
        # find correct cost combinations for current total cost
        concat_set = set()
        concat_list = []
        replace_set = set()
        replace_list = []
        for i in self.plist.keys():
            for j in self.plist.keys():
                if i + j + self.grammar_costs['concat'] == self.current_cost:
                    new_tuple = tuple(sorted([i,j]))
                    if new_tuple not in concat_set:
                        concat_set.add(new_tuple)
                        concat_list.append(new_tuple)
                for k in self.plist.keys():
                    if i + j + k + self.grammar_costs['replace'] == self.current_cost:
                        new_tuple = tuple(sorted([i,j,k]))
                        if new_tuple not in replace_set:
                            replace_set.add(new_tuple)
                            replace_list.append(new_tuple)
        
        # go through replace_set
        for (size1,size2,size3) in tqdm(replace_list):
            for i in self.plist[size1]:
                for j in self.plist[size2]:
                    for k in self.plist[size3]:
                        yield Replace(i, j, k)
                        yield Replace(i, k, j)
                        yield Replace(j, i, k)
                        yield Replace(j, k, i)
                        yield Replace(k, i, j)
                        yield Replace(k, j, i)
        
        # go through concat_set
        for (size1,size2) in tqdm(concat_list):
            for i in self.plist[size1]:
                for j in self.plist[size2]:
                    yield Concat(i, j)
                    yield Concat(j, i)
        
    def update_grammar_costs(self):
        # equal probabilities
        p_u = 1 / len(self.grammar)
        # initialize array of probabilities
        pcfg_probs_array = np.zeros(len(self.grammar))
        # get 'max' part from paper cost update equation
        for i,key in enumerate(self.grammar.keys()):
            if key == '':
                rule_str = 'BLANK'
            else:
                rule_str = key
            max_occ = 0
            for (p, sst) in self.partial_solutions:
                if rule_str in p.toString():
                    if sum(sst) > max_occ:
                        max_occ = sum(sst)
            pcfg_probs_array[i] = p_u**(1 - (max_occ / len(self.in_out)))
        # normalize probabilities to sum to 1
        pcfg_probs_array = pcfg_probs_array / np.sum(pcfg_probs_array)
        # update grammar costs
        for i,key in enumerate(self.grammar.keys()):
            self.grammar_costs[key] = round(-math.log2(pcfg_probs_array[i]))
        print(self.grammar_costs)


# input-output pairs
in_out = [{'arg': 'a < 4 and a > 0', 'out': 'a  4 and a  0'},
          {'arg': '<open and <close>', 'out': 'open and close'},
          {'arg': '<change> <string> to <a> number', 'out': 'change string to a number'}]

# uncosted grammar
grammar = {
    'arg':     Var('arg'),
    '':        Str(''),
    '<':       Str('<'),
    '>':       Str('>'),
    'replace': Replace,
    'concat':  Concat,
    }

# RUN
start_time = time.time()
synthesizer = GBUS(grammar=grammar, in_out=in_out, bound=100,
                   pcfg_start='equal', update_pcfg=True)
p = synthesizer.run_search()
print('\nSolution:')
print(p.toString())
print('\nTime:')
print(time.time() - start_time)
print('\nNumber of programs:')

num_progs = 0
for cost, cost_plist in synthesizer.plist.items():
    print(f'Cost {cost}: {len(cost_plist)}')
    num_progs += len(cost_plist)

print(f'Total: {num_progs}')
print(f'True total: {synthesizer.total_progs_eval}')

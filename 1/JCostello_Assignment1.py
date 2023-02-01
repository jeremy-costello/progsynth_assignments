# some imports
import time
from collections import Counter
from sympy import sympify, SympifyError

# parent class of nodes on the tree (parts of the CFG)
class Node:
    # converts program to a string
    def toString(self):
        raise Exception('Unimplemented method')
    
    # interprets the output of a program
    # env is a dict of variable values
    def interpret(self):
        raise Exception('Unimplemented method')
        
    # grow the program for BUS
    def grow(self, plist, new_plist):
        pass

# not
class Not(Node):
    def __init__(self, left):
        self.left = left

    def toString(self):
        return 'not (' + self.left.toString() + ')'

    def interpret(self, env):
        return not (self.left.interpret(env))

    def grow(LT_list, LT_list_len):
        pass

# and
class And(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " and " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) and self.right.interpret(env)

    def grow(LT_list, LT_list_len):
        pass
        

# less than
class Lt(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " < " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) < self.right.interpret(env)

    def grow(plist, LT_list, LT_list_len):
        # loop over every program in the plist
        for i,p1 in enumerate(plist):
            # only accept a program without 'if's
            # check if min program length is less than or equal to size
            if 'if' not in p1.toString() and synthesizer.plist_size[i] + 4 <= synthesizer.size:
                # loop over all programs in plist >= i
                # Lt is symmetric, so only have to loop over half
                for j,p2 in enumerate(plist[i:]):
                    if 'if' not in p2.toString() and synthesizer.plist_size[i] + synthesizer.plist_size[i+j] + 3 <= synthesizer.size:
                        # append program to list of less than programs
                        LT_list.append(Lt(p1, p2))
                        # list of length of each less than program
                        LT_list_len.append(synthesizer.plist_size[i] + synthesizer.plist_size[i+j] + 1)
                        LT_list.append(Lt(p2, p1))
                        LT_list_len.append(synthesizer.plist_size[i] + synthesizer.plist_size[i+j] + 1)
                            
        return LT_list, LT_list_len

# if then else
class Ite(Node):
    def __init__(self, condition, true_case, false_case):
        self.condition = condition
        self.true_case = true_case
        self.false_case = false_case

    def toString(self):
        return "(if " + self.condition.toString() + " then " + self.true_case.toString() + " else " + self.false_case.toString() + ")"

    def interpret(self, env):
        if self.condition.interpret(env):
            return self.true_case.interpret(env)
        else:
            return self.false_case.interpret(env)

    def grow(plist, new_plist):
        # create lists of less than programs and their lengths
        LT_list = []
        LT_list_len = []
        LT_list, LT_list_len = Lt.grow(plist, LT_list, LT_list_len)
        # loop over first program
        for i,p1 in enumerate(plist):
            # check if min program size still fits within level size
            if synthesizer.plist_size[i] + 5 <= synthesizer.size:
                # loop over second program
                # symmetry allows looping over programs with index equal or greater than p1
                for j,p2 in enumerate(plist[i:]):
                    if synthesizer.plist_size[i] + synthesizer.plist_size[i+j] + 4 <= synthesizer.size:
                        # loop over first less than program
                        for k,b1 in enumerate(LT_list):
                            if synthesizer.plist_size[i] + synthesizer.plist_size[i+j] + LT_list_len[k] + 1 <= synthesizer.size:
                                # check if program size is correct before appending
                                if synthesizer.plist_size[i] + synthesizer.plist_size[i+j] + LT_list_len[k] + 1 == synthesizer.size:
                                    new_plist.append(Ite(b1, p1, p2))
                                    new_plist.append(Ite(b1, p2, p1))
                                elif synthesizer.plist_size[i] + synthesizer.plist_size[i+j] + LT_list_len[k] + 2 <= synthesizer.size:
                                    # check if 'Not' is in the CFG and program size is correct
                                    if Not in synthesizer.intops_B and synthesizer.plist_size[i] + \
                                        synthesizer.plist_size[i+j] + LT_list_len[k] + 2 == synthesizer.size:
                                        ''''''
                                        new_plist.append(Ite(Not(b1), p1, p2))
                                        new_plist.append(Ite(Not(b1), p2, p1))
                                    # check if 'And' is in the CFG and min program length is within bound
                                    if And in synthesizer.intops_B and synthesizer.plist_size[i] \
                                        + synthesizer.plist_size[i+j] + LT_list_len[k] + 5 <= synthesizer.size:
                                        ''''''
                                        # loop over second less than program (symmetry again)
                                        for l,b2 in enumerate(LT_list[k:]):
                                            # check if program size is correct
                                            if synthesizer.plist_size[i] + synthesizer.plist_size[i+j] + \
                                                LT_list_len[k] + LT_list_len[k+l] + 2 == synthesizer.size:
                                                ''''''
                                                # append all valid combinations of p1,p2,b1,b2
                                                # only need two since 'And' is commutative
                                                new_plist.append(Ite(And(b1, b2), p1, p2))
                                                new_plist.append(Ite(And(b1, b2), p2, p1))
        return new_plist

# number
class Num(Node):
    def __init__(self, value):
        self.value = value

    def toString(self):
        return str(self.value)

    def interpret(self, env):
        return self.value

# variable
class Var(Node):
    def __init__(self, name):
        self.name = name

    def toString(self):
        return self.name

    def interpret(self, env):
        return env[self.name]

# addition
class Plus(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " + " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) + self.right.interpret(env)

    def grow(plist, new_plist):
        # loop over first program
        for i,p1 in enumerate(plist):
            # loop over second program (symmetry)
            for j,p2 in enumerate(plist[i:]):
                # check if program size is correct
                if synthesizer.plist_size[i] + synthesizer.plist_size[i+j] + 1 == synthesizer.size:
                    # only need one symmetric program since addition is commutative
                    new_plist.append(Plus(p1, p2))
        return new_plist

# multiplication
class Times(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " * " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) * self.right.interpret(env)
    
    def grow(plist, new_plist):
        # loop over first program
        for i,p1 in enumerate(plist):
            # loop over second program (symmetry)
            for j,p2 in enumerate(plist[i:]):
                # check if program size is correct
                if synthesizer.plist_size[i] + synthesizer.plist_size[i+j] + 1 == synthesizer.size:
                    # only need one symmetric program since multiplication is commutative
                    new_plist.append(Times(p1, p2))
        return new_plist


# BUS class
class BottomUpSearch():
    '''
    Bottom Up Search (BUS) class.
    '''
    
    def grow(self, plist, intops_S):
        '''

        Parameters
        ----------
        plist : list of programs
            all non-equivalent (weak) programs found so far.
        intops_S : list of functions
            Functions in the 'S' class of the Context-Free Grammar (CFG).

        Returns
        -------
        plist : list of programs
            all non-equivalent (weak) programs found so far.

        '''
        # emtpy list of new programs found in this cycle
        nplist = []
        # loop over and grow all operations
        for op in intops_S:
            nplist = op.grow(plist, nplist)
        self.progs_created += len(nplist)
        # check for weak equivalence with existing programs
        for p in nplist:
            out_tuple = tuple()
            for in_out in self.input_output:
                out_tuple += (p.interpret(in_out),)
            if out_tuple not in self.output:
                self.output.add(out_tuple)
                plist.append(p)
                self.plist_size.append(self.size)
        return plist

    def synthesize(self, bound, intops_S, intops_B, intvals, variables, input_output):
        '''
        
        Parameters
        ----------
        bound : integer
            Largest program size to search for.
        intops_S : list of functions
            Functions in the 'S' class of the CFG.
        intops_B : list of functions
            Functions in the 'B' class of the CFG.
        intvals : list of integers
            Integer values in the CFG.
        variables : list of strings
            Variables in the CFG.
        input_output : list of dicts
            Input-output pairs to check over.

        Returns
        -------
        plist[j] : a program
            The first program to correctly solve all input-output pairs.

        '''
        # create selfs for class
        self.intops_S = intops_S
        self.intops_B = intops_B
        self.input_output = input_output
        self.size = 1 # current program size (search by increasing sizes)
        self.output = set() # set of all outputs found so far
        
        # get correct output tuple
        self.correct_tuple = tuple()
        for in_out in self.input_output:
            self.correct_tuple += (in_out['out'],)
        
        # create plist
        plist = []
        for intval in intvals:
            plist.append(Num(intval))
        for var in variables:
            plist.append(Var(var))
        # list of the size of each program in plist
        self.plist_size = [self.size] * len(plist)
        
        # track number of programs
        self.progs_created = len(plist)
        self.progs_evaluated = 0
        
        # loop over programs
        while self.size < bound:
            self.size += 1
            plist = self.grow(plist, intops_S)
            # evaluate programs which haven't been evaluated yet
            for j in range(self.progs_evaluated, len(plist)):
                self.progs_evaluated += 1
                out_tuple = tuple()
                for in_out in self.input_output:
                    out_tuple += (plist[j].interpret(in_out),)
                # check if all outputs are correct
                if out_tuple == self.correct_tuple:
                    self.plist = plist
                    return plist[j]


# BFS class
class BreadthFirstSearch():
    '''
    Breadth-First Search (BFS) class.
    '''
    def children(self, old_prog):
        '''
        
        Parameters
        ----------
        old_prog : list
            The program list with which to create children.

        Returns
        -------
        bool
            Whether a correct solution was found.
        program or placeholder string
            Returns the correct program if found, otherwise placeholder string.

        '''
        # loop over each section of the parent ('old') program
        for i in range(len(old_prog)):
            # find leftmost non-terminal symbol
            if old_prog[i] in ['B', 'S', 'PTL', 'NA']:
                # for each operation in the corresponding part of the CFG
                for adder in self.ops[old_prog[i]]:
                    self.progs_created += 1
                    # create a new program by removing non-terminal symbol and adding new operation
                    prog = list(old_prog[:i]) + list(adder) + list(old_prog[i+1:])
                    # if there are no non-terminal symbols in the new program
                    if 'S' not in prog and 'B' not in prog and 'PTL' not in prog and 'NA' not in prog:
                        initial_len = len(prog)
                        self.old_len = initial_len
                        # transform list of program parts to runnable program
                        for i in range(initial_len):
                            idx = initial_len - i - 1
                            if prog[idx] in [Ite]:
                                prog[idx] = prog[idx](prog.pop(idx+1), prog.pop(idx+1), prog.pop(idx+1))
                            elif prog[idx] in [Plus, Times, Lt, And]:
                                prog[idx] = prog[idx](prog.pop(idx+1), prog.pop(idx+1))
                            elif prog[idx] in [Not]:
                                prog[idx] = prog[idx](prog.pop(idx+1))
                            else:
                                pass
                        self.progs_evaluated += 1
                        # get outputs for current program
                        out_tuple = tuple()
                        for in_out in self.input_output:
                            out_tuple += (prog[0].interpret(in_out),)
                        # check if all outputs are correct
                        if out_tuple == self.correct_tuple:
                            return True, prog[0]
                    # if there are still non-terminal symbols
                    else:
                        # count of each item in program list
                        count = Counter(prog)
                        # 'B' and 'NA' add at least 2 to program length per occurrence
                        min_true_len = len(prog) + 2 * (count['B'] + count['NA'])
                        # check if minimum potential program size is within bound
                        if min_true_len <= self.bound:
                            # purge (some) duplicate programs up to some arbitrary size
                            # (bound - 4) worked best from the tests I did
                            duplicate_check_max = self.bound - 4
                            if self.old_len <= duplicate_check_max:
                                sym_str = self.check_sympy_output(prog)
                                # check if sympy output already found
                                if sym_str not in self.output:
                                    self.output.add(sym_str)
                                    self._open.append(prog)
                            # if size is greater than cutoff, add program to _open
                            else:
                                self._open.append(prog)
                # break loop once first non-terminal symbol is found
                break
        return False, '_'
    
    def check_sympy_output(self, prog):
        # only checks strong equivalence currently
        # can probably make it check weak equivalence
        # replace variables with actual values from input-output pairs
        ## Var('x') -> Num(input_output['x'])
        # do this for each input-output pair
        # save output as a tuple of strings
        '''
        
        Parameters
        ----------
        prog : list
            The program list to check for equivalence with sympy.

        Returns
        -------
        string
            The sympy-equivalent program string.

        '''
        # copy the program list (probably not needed)
        prog_test = prog.copy()
        # replace CFG variables with lowercase Var() for sympy
        for x in range(len(prog_test)):
            if prog_test[x] == 'PTL' or prog_test[x] == 'S':
                prog_test[x] = Var('s')
            elif prog_test[x] == 'NA' or prog_test[x] == 'B':
                prog_test[x] = Var('b')
        
        # transform list of program parts to sympy string
        initial_len_test = len(prog_test)
        for i in range(initial_len_test):
            idx = initial_len_test - i - 1
            if prog_test[idx] in [Ite]:
                prog_test[idx] = Var(prog_test[idx](prog_test.pop(idx+1), prog_test.pop(idx+1), prog_test.pop(idx+1)).toString())
            elif prog_test[idx] in [Plus, Times]:
                input_1 = prog_test.pop(idx+1)
                input_2 = prog_test.pop(idx+1)
                try:
                    prog_test[idx] = Var(str(sympify(prog_test[idx](input_1, input_2).toString())))
                except SympifyError:
                    prog_test[idx] = Var(prog_test[idx](input_1, input_2).toString())
            elif prog_test[idx] in [Lt, And]:
                prog_test[idx] = Var(prog_test[idx](prog_test.pop(idx+1), prog_test.pop(idx+1)).toString())
            elif prog_test[idx] in [Not]:
                prog_test[idx] = Var(prog_test[idx](prog_test.pop(idx+1)).toString())
            else:
                pass
        # string of sympy output of program string
        sym_str = prog_test[0].toString()
        return sym_str
    
    def synthesize(self, bound, intops_S, intops_B, intvals, variables, input_output):
        '''
        
        Parameters
        ----------
        bound : integer
            Largest program size to search for.
        intops_S : list of functions
            Functions in the 'S' class of the CFG.
        intops_B : list of functions
            Functions in the 'B' class of the CFG.
        intvals : list of integers
            Integer values in the CFG.
        variables : list of strings
            Variables in the CFG.
        input_output : list of dicts
            Input-output pairs to check over.

        Returns
        -------
        solution : a program
            The first program to correctly solve all input-output pairs.

        '''
        # some selfs
        self.input_output = input_output
        self.bound = bound
        self.old_len = 0 # length of most recently evaluated program
        self.output = set() # list of sympy program strings found so far
        
        # get correct output tuple
        self.correct_tuple = tuple()
        for in_out in self.input_output:
            self.correct_tuple += (in_out['out'],)
        
        # create operation dict
        ### PTL ops (Plus, Times, Less than)
        PTL_list = [[Var(x)] for x in variables] + [[Num(x)] for x in intvals]
        if Plus in intops_S:
            PTL_list += [[Plus, 'PTL', 'PTL']]
        if Times in intops_S:
            PTL_list += [[Times, 'PTL', 'PTL']]
        ### S ops
        S_list = PTL_list
        if Ite in intops_S:
            S_list += [[Ite, 'B', 'S', 'S']]
        ### NA ops (Not, And)
        NA_list = []
        if Lt in intops_B:
            NA_list += [[Lt, 'PTL', 'PTL']]
        ### B ops
        B_list = NA_list
        if And in intops_B:
            B_list += [[And, 'NA', 'NA']]
        if Not in intops_B:
            B_list += [[Not, 'NA']]
        
        self.ops = {
                    'S':   S_list,
                    'B':   B_list,
                    'PTL': PTL_list,
                    'NA':  NA_list,
                    }
        
        # all eligible programs which haven't had children made
        self._open = ['S']
        # number of programs created so far
        self.progs_created = 1
        # number of programs evaluated so far
        self.progs_evaluated = 0
        # while _open isn't empty and the bound hasn't been exceeded
        while self._open and len(self._open[0]) <= bound:
            # parent program is first in _open (FiFo)
            p = self._open.pop(0)
            solved, solution = self.children(p)
            # if 'solution' correctly solved all input-output pairs
            if solved:
                return solution


# problem 1
def p1(synthesizer):
    p1_soln = synthesizer.synthesize(6, [Ite], [Lt], [1, 2], ['x', 'y'],
                                     [{'x':5, 'y': 10, 'out':5},
                                      {'x':10, 'y': 5, 'out':5},
                                      {'x':4, 'y': 3, 'out':3}])
    
    return p1_soln.toString(), synthesizer.progs_created, synthesizer.progs_evaluated

# problem 2
def p2(synthesizer):
    p2_soln = synthesizer.synthesize(12, [Plus, Times, Ite], [Lt, Not, And], [10], ['x', 'y'],
                                     [{'x':5, 'y': 10, 'out':5},
                                      {'x':10, 'y': 5, 'out':5},
                                      {'x':4, 'y': 3, 'out':4},
                                      {'x':3, 'y': 4, 'out':4}])
    
    return p2_soln.toString(), synthesizer.progs_created, synthesizer.progs_evaluated

# problem 3
def p3(synthesizer):
    p3_soln = synthesizer.synthesize(10, [Plus, Times, Ite], [Lt, Not, And], [-1, 5], ['x', 'y'],
                                     [{'x':10, 'y':7, 'out':17},
                                      {'x':4, 'y':7, 'out':-7},
                                      {'x':10, 'y':3, 'out':13},
                                      {'x':1, 'y':-7, 'out':-6},
                                      {'x':1, 'y':8, 'out':-8}])
    
    return p3_soln.toString(), synthesizer.progs_created, synthesizer.progs_evaluated
    
# solve all problems with BUS and BFS, print some results
# this takes ~5 minutes on my computer
for prob in [p1, p2, p3]:
    for synthesizer_name in ['BUS', 'BFS']:
        if synthesizer_name == 'BUS':
            synthesizer = BottomUpSearch()
        elif synthesizer_name == 'BFS':
            synthesizer = BreadthFirstSearch()
        start_time = time.time()
        soln, progs_cre, progs_eval = prob(synthesizer)
        print(f'{prob.__name__} / {synthesizer_name} :')
        print(f'{round(time.time() - start_time, 3)} seconds')
        print(f'{progs_cre} programs created; {progs_eval} programs evaluated.')
        print(f'{soln}\n')
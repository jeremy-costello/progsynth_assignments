import time
from DSL import *
from main_starter import play_n_matches
from tqdm import tqdm
from rule_of_28_sketch import Rule_of_28_Player_PS

class DSBUS:
    def __init__(self, size_bound, ibr_bound, grammar_constants, search_for):
        '''
        
        Parameters
        ----------
        size_bound : integer
            max program size to search for.
        ibr_bound : integer
            max number of IBR iterations.
        grammar_constants : dict
            dictionary of the grammar.

        Returns
        -------
        None.

        '''
        # assert search_for is in correct range
        assert search_for in ['both', 'column']
        # selfs
        self.size_bound = size_bound
        self.ibr_bound = ibr_bound
        self.grammar_constants = grammar_constants
        self.search_for = search_for
    
    # challenge the player from 'main_starter'
    def final_challenge(self):
        pyn = Sum(Map(Function(Times(Plus(NumberAdvancedThisRound(), Constant(1)), VarScalarFromArray('progress_value'))), VarList('neutrals')))
        pdc = Argmax(Map(Function(Sum(Map(Function(Minus(Times(NumberAdvancedByAction(), VarScalarFromArray('move_value')), Times(VarScalar('marker'), IsNewNeutral()))), None))), VarList('actions')))
        final_boss = Rule_of_28_Player_PS(pyn, pdc)
        brv, bossv = play_n_matches(self.best_response, final_boss, 1000)
        print('----------')
        print('BOSS FIGHT!')
        print(brv, bossv)
        print('Found BR: ', brv / (brv + bossv))
        print('Boss: ', bossv / (brv + bossv))
        print('----------')
    
    # triage strategy evaluation
    def triage_eval(self, program_yes_no, program_decide_column):
        '''
        
        Parameters
        ----------
        program_yes_no : program
            program to decide whether to keep playing.
        program_decide_column : program
            program to decide column to play.

        Returns
        -------
        None.

        '''
        challenger = Rule_of_28_Player_PS(program_yes_no, program_decide_column)
        # find initial strategy
        if self.ibr_iteration < 0:
            (p1v, p2v) = play_n_matches(challenger, challenger, 50)
            self.progs_evaled += 1
            if (p1v + p2v) >= 60:
                self.ibr_iteration += 1
                self.best_response = challenger
                self.program_decide_column = program_decide_column
                self.program_yes_no = program_yes_no
                # tqdm will mess up prints if a small pause is not taken before/after
                time.sleep(0.2)
                print(f'\nIBR iteration: {self.ibr_iteration}')
                print(f'Decisive matches: {p1v + p2v}')
                print('yes-no decision program:')
                print(program_yes_no.toString())
                print('column decision program')
                print(program_decide_column.toString())
                self.final_challenge()
        # find IBR strategies
        else:
            total_challenger_wins = 0
            total_best_response_wins = 0
            (chv, brv) = play_n_matches(challenger, self.best_response, 5)
            self.progs_evaled += 1
            total_challenger_wins += chv
            total_best_response_wins += brv
            # wins 20% of first 10 matches
            if total_challenger_wins / (total_challenger_wins + total_best_response_wins) >= 0.2:
                (chv, brv) = play_n_matches(challenger, self.best_response, 95)
                total_challenger_wins += chv
                total_best_response_wins += brv
                # wins 55% of first 200 matches
                if total_challenger_wins / (total_challenger_wins + total_best_response_wins) >= 0.55:
                    (chv, brv) = play_n_matches(challenger, self.best_response, 400)
                    total_challenger_wins += chv
                    total_best_response_wins += brv
                    # wins 55% of first 1000 matches
                    if total_challenger_wins / (total_challenger_wins + total_best_response_wins) >= 0.55:
                        self.ibr_iteration += 1
                        self.best_response = challenger
                        self.program_decide_column = program_decide_column
                        self.program_yes_no = program_yes_no
                        time.sleep(0.2)
                        print(f'\nIBR iteration: {self.ibr_iteration}')
                        print('Challenger win rate:')
                        print(total_challenger_wins / (total_challenger_wins + total_best_response_wins))
                        print('yes-no decision program:')
                        print(program_yes_no.toString())
                        print('column decision program')
                        print(program_decide_column.toString())
                        self.final_challenge()
    
    def search(self):
        # number of programs generated
        self.progs_generated = 0
        
        # initial strategy
        if self.search_for == 'column':
            self.program_yes_no = Sum(Map(Function(Times(Plus(NumberAdvancedThisRound(), Constant(1)), VarScalarFromArray('progress_value'))), VarList('neutrals')))
        elif self.search_for == 'both':
            self.program_yes_no = None
        self.program_decide_column = None
        
        # IBR iteration and best response
        self.ibr_iteration = -1
        self.best_response = None
        
        # initial plist
        self.plist_noeval = {}
        self.plist_noeval['l'] = {}
        self.plist_noeval['e'] = {}
        self.plist_noeval['s'] = {}
        self.plist_noeval['l'][1] = self.grammar_constants['l']
        self.plist_noeval['e'][1] = self.grammar_constants['s']
        self.plist_noeval['s'][1] = self.grammar_constants['s']
        
        # starting search size
        self.current_size = 1
        
        # update number of programs generated
        self.progs_generated += len(self.plist_noeval['l'][self.current_size])
        self.progs_generated += len(self.plist_noeval['e'][self.current_size])
        self.progs_generated += len(self.plist_noeval['s'][self.current_size])
        
        # the search
        while (self.current_size < self.size_bound) and (self.ibr_iteration < self.ibr_bound):
            self.progs_evaled = 0
            self.current_size += 1
            print('**********')
            print(f'PROGRAM SIZE: {self.current_size}')
            # get all new 'Argmax' and 'Sum' strats (if needed)
            argmax_list, sum_list = self.generate_new_programs()
            # tqdm will mess up prints if a small pause is not taken before/after
            time.sleep(0.2)
            if self.ibr_iteration < 0:
                for program_decide_column in tqdm(argmax_list):
                    for program_yes_no in sum_list:
                        # some programs don't work, so use a try-except block
                        try:
                            self.triage_eval(program_yes_no, program_decide_column)
                        except:
                            pass
                time.sleep(0.2)
            else:
                # only search over yes_no strategies if required
                if self.search_for == 'both':
                    for program_yes_no in tqdm(sum_list):
                        try:
                            self.triage_eval(program_yes_no, self.program_decide_column)
                        except:
                            pass
                time.sleep(0.2)
                for program_decide_column in tqdm(argmax_list):
                    try:
                        self.triage_eval(self.program_yes_no, program_decide_column)
                    except:
                        pass
            time.sleep(0.2)
            print(f'PROGRAMS EVALUATED: {self.progs_evaled}')
    
    # generate new programs
    def generate_new_programs(self):       
        # strategy lists
        argmax_list = []
        sum_list = []
        
        ### lists
        # argmax, sum
        as_set = set()
        as_list = []
        # plus, times, minus
        ptm_set = set()
        ptm_list = []
        # map
        map_set = set()
        map_list = []
        # map, None
        mapnone_set = set()
        mapnone_list = []
        
        ### valid program sizes
        # argmax, sum
        for size1 in self.plist_noeval['l'].keys():
            if size1 + 1 == self.current_size:
                new_tuple = size1
                if new_tuple not in as_set:
                    as_set.add(new_tuple)
                    as_list.append(new_tuple)
        # plus, times, minus
        for size1 in self.plist_noeval['s'].keys():
            for size2 in self.plist_noeval['s'].keys():
                if size1 + size2 + 1 == self.current_size:
                    new_tuple = tuple((size1, size2))
                    if new_tuple not in ptm_set:
                        ptm_set.add(new_tuple)
                        ptm_list.append(new_tuple)
        # map
        for size1 in self.plist_noeval['e'].keys():
            for size2 in self.plist_noeval['l'].keys():
                if size1 + size2 + 2 == self.current_size:
                    new_tuple = tuple((size1, size2))
                    if new_tuple not in map_set:
                        map_set.add(new_tuple)
                        map_list.append(new_tuple)
        # map, None
        for size1 in self.plist_noeval['e'].keys():
            if size1 + 2 == self.current_size:
                new_tuple = size1
                if new_tuple not in mapnone_set:
                    mapnone_set.add(new_tuple)
                    mapnone_list.append(new_tuple)
        
        ### create new lists in program list if needed
        if as_list or ptm_list or map_list or mapnone_list:
            self.plist_noeval['e'][self.current_size] = []
        if map_list or mapnone_list:
            self.plist_noeval['l'][self.current_size] = []
        
        ### generate programs
        # argmax, sum
        for size1 in as_list:
            for l in self.plist_noeval['l'][size1]:
                argmax_list.append(Argmax(l))
                # only add to 'sum list' if searching for both strategies
                if self.search_for == 'both':
                    sum_list.append(Sum(l))
                self.plist_noeval['e'][self.current_size].append(Sum(l))
        # plus, times, minus
        for (size1, size2) in ptm_list:
            for s1 in self.plist_noeval['s'][size1]:
                for s2 in self.plist_noeval['s'][size2]:
                    self.plist_noeval['e'][self.current_size].append(Plus(s1, s2))
                    self.plist_noeval['e'][self.current_size].append(Times(s1, s2))
                    self.plist_noeval['e'][self.current_size].append(Minus(s1, s2))
        # map
        for (size1, size2) in map_list:
            for e in self.plist_noeval['e'][size1]:
                for l in self.plist_noeval['l'][size2]:
                    self.plist_noeval['e'][self.current_size].append(Map(Function(e), l))
                    self.plist_noeval['l'][self.current_size].append(Map(Function(e), l))
        # map, None
        for size in mapnone_list:
            for e in self.plist_noeval['e'][size1]:
                self.plist_noeval['e'][self.current_size].append(Map(Function(e), None))
                self.plist_noeval['l'][self.current_size].append(Map(Function(e), None))
        
        # update number of programs generated
        if as_list or ptm_list or map_list or mapnone_list:
            self.progs_generated += len(self.plist_noeval['e'][self.current_size])
            self.progs_generated += len(argmax_list)
            self.progs_generated += len(sum_list)
        if map_list or mapnone_list:
            self.progs_generated += len(self.plist_noeval['l'][self.current_size])
        
        ### return
        if self.search_for == 'both':
            return argmax_list, sum_list
        elif self.search_for == 'column':
            return argmax_list, [self.program_yes_no]
             

# grammar
grammar_constants = {}
grammar_constants['l'] = [VarList('neutrals'), VarList('actions')]
grammar_constants['s'] = [VarScalarFromArray('progress_value'),
                          VarScalarFromArray('move_value'),
                          NumberAdvancedThisRound(), NumberAdvancedByAction(),
                          IsNewNeutral(), VarScalar('marker'), Constant(1)]

### INPUTS
size_bound = 11
ibr_bound = 5
search_for = 'both'

# running the search
synthesizer = DSBUS(size_bound, ibr_bound, grammar_constants, search_for)
synthesizer.search()
print('TOTAL PROGRAMS GENERATED:')
print(synthesizer.progs_generated)
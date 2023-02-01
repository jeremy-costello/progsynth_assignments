import random
import time
from game import Game
from random_player import RandomPlayer
from rule_of_28_sketch import Rule_of_28_Player_PS
from DSL import *

def play_match(p1, p2):
    game = Game(n_players = 2, dice_number = 4, dice_value = 6, column_range = [2,12],
                offset = 2, initial_height = 3)
    
    is_over = False
    who_won = None

    number_of_moves = 0
    current_player = game.player_turn
    while not is_over:
        moves = game.available_moves()
        if game.is_player_busted(moves):
            if current_player == 1:
                current_player = 2
            else:
                current_player = 1
            continue
        else:
            if game.player_turn == 1:
                chosen_play = p1.get_action(game)
            else:
                chosen_play = p2.get_action(game)
            if chosen_play == 'n':
                if current_player == 1:
                    current_player = 2
                else:
                    current_player = 1
            game.play(chosen_play)
            number_of_moves += 1
        who_won, is_over = game.is_finished()
        
        if is_over:
            return is_over, who_won
        
        if number_of_moves >= 300:
            #print('Draw!')
            return False, None

def play_n_matches(p1, p2, n):
    
    p1_victories = 0
    p2_victories = 0
    
    for _ in range(n):
        # plays a match with br as player 1
        finished, who_won = play_match(p1, p2)
        
        if finished:
            if who_won == 1:
                p1_victories += 1
            else:
                p2_victories += 1
        
        # plays another match with br as player 2        
        finished, who_won = play_match(p2, p1)
        
        if finished:
            if who_won == 1:
                p2_victories += 1
            else:
                p1_victories += 1
    
    return p1_victories, p2_victories


if __name__ == "__main__":    
    
    program_yes_no = Sum(Map(Function(Times(Plus(NumberAdvancedThisRound(), Constant(1)), VarScalarFromArray('progress_value'))), VarList('neutrals')))
    program_decide_column = Argmax(Map(Function(Sum(Map(Function(Minus(Times(NumberAdvancedByAction(), VarScalarFromArray('move_value')), Times(VarScalar('marker'), IsNewNeutral()))), None))), VarList('actions')))
    
    pyn2 = Sum(Map(Function(Map(Function(Times(NumberAdvancedThisRound(), NumberAdvancedThisRound())), VarList('neutrals'))), VarList('actions')))
    pdc2 = Argmax(Map(Function(Sum(Map(Function(VarScalarFromArray('move_value')), None))), VarList('actions')))
       
    p1 = RandomPlayer()
    p1 = Rule_of_28_Player_PS(pyn2, pdc2)
    p2 = Rule_of_28_Player_PS(program_yes_no, program_decide_column)
    
    victories1 = 0
    victories2 = 0
    
    start = time.time()
    
    victories1, victories2 = play_n_matches(p1, p2, 50000) #500
            
    end = time.time()
    print(victories1, victories2)
    print('Player 1: ', victories1 / (victories1 + victories2))
    print('Player 2: ', victories2 / (victories1 + victories2))
    print(end - start, ' seconds')


#####################################################################
##                    Probabilistic CKY Parser                     ## 
##                                                                 ## 
#####################################################################


#####################################################################
# File:                           CKYProbabilisticParser.py         #
# Author:                         Aline Castendiek                  #
# Student ID:                     768297                            #
# Date:                           30/10/14                          #
# 1st operating system:           Windows 7 [6.1.7601]              #
# 2nd operating system:           Linux Mint 17 Qiana[Ubuntu 14.04] #
#####################################################################


#####################################################################
#              NLTK is only used for two purposes:                  #   
#                 1) its grammar implementation                     #
#                 2) its tree representations                       #
#####################################################################

import nltk.grammar
from nltk.tree import Tree

# Represents a probabilistic CKY parser that computes the most probable parse 
# tree for an input sentence. Takes the grammar as constructor argument. To
# compute the trees for an input, the class function prob_cky_parse(words) that 
# takes the input as argument is called inside the main function.    
class ProbCKYParser(object):
    def __init__(self, grammar):
        self.grammar = grammar
        self.matrix = []


#####################################################################
#                     Probabilistic CKY Parse                       #
#####################################################################

    # Parses an input sentence and returns the most likely tree for it.
    def prob_cky_parse(self, words):

        # Length of input sentence:
        n = len(words)
        # Create an array as basis for matrix:
        self.matrix = []
        
        # Starting at cell [0][0], create matrix and fill each cell with a dictionary.
        for i in range(n):
            # Create another array:
            row = []
            for j in range(n):
                # Append the empty dictionaries to this other array first:
                row.append({})
            # Then append this array to the already existing array to create the two-dimensional matrix: 
            self.matrix.append(row)
        
        # For each terminal symbol in input words: 
        for i in range(n):
            # For every terminal add nonterminal respectively:
            for prod in self.grammar.productions(rhs=words[i]):
                # Create quadruple consisting of the word, two zeros and its probability
                # (I added the two zeros to avoid indexing errors later on)
                self.matrix[i][0][prod.lhs()] = (words[i],0,0,prod.prob())      
                
        for j in range(2, n+1):                            # j: span length
            for i in range(n-j+1):                         # i: start of span
                for k in range(1, j):                      # k: partition of span
                    
                    nts1 = self.matrix[i][k-1]             # nts1: first nonterminal symbol
                    nts2 = self.matrix[i+k][j-k-1]         # nts2: second nonterminal symbol
                    
                    # For all nonterminals in nts1:
                    for nt1 in nts1:
                        # productions: rule where nts1 is on the right side of the production
                        productions = self.grammar.productions(rhs=nt1)
                        
                        # for all above declared production rules:
                        for production in productions:
                            if len(production.rhs()) == 2:
                            # If nts2 is in the second position on the right side of the production
                            # (counting starts from zero, therefore position[0] = first position, [1] = second position etc.)
                                if production.rhs()[1] in nts2:
                                    # Create quadruple consisting of both nonterminals, span and a zero
                                    self.matrix[i][j-1][production.lhs()] = (nt1, production.rhs()[1], k, 0)
                                   
                                    # For all nonterminals in nts2:
                                    for nt2 in nts2:
                                        # Probability of first nonterminal on right hand side of production:
                                        nt1_probability = self.matrix[i][k-1][nt1][3]
                                        # Probability of second nonterminal on right hand side of production:
                                        nt2_probability = self.matrix[i+k][j-k-1][nt2][3]
                                        
                                        # The probability of a subtree is computed by multiplying production rule probability,
                                        # probability of first nonterminal and second nonterminal:
                                        subtree_prob = production.prob() * nt1_probability * nt2_probability
                                        
                                        # If the subtree probability exceeds the probability value already stored in corresponding
                                        # matrix cell (which only contains a zero at the beginning), then store the new, larger probability. 
                                        if subtree_prob > self.matrix[i][j-1][production.lhs()][3]:
                                            old_tuple = self.matrix[i][j-1][production.lhs()] 
                                            # Creating a new tuple to change the stored probability because tuples are immutable:
                                            new_tuple = (old_tuple[0], old_tuple[1], old_tuple[2], subtree_prob)
                                            
                                            # Replace old tuple and write new tuple in correspondent matrix cell:
                                            self.matrix[i][j-1][production.lhs()] = new_tuple     
        
        # Now we construct the syntax tree top-down. Starting at matrix cell 
        # [0][n-1] which is the root node of the tree:
        for nonterminal in self.matrix[0][n-1]:

            # If the nonterminal is a start symbol:
            if nonterminal == self.grammar.start():
                # Probability of whole tree:
                tree_probability = self.matrix[0][n-1][nonterminal][3]  
                # Recusively constructed tree:    
                syntax_tree =  self.get_tree(0,n-1,nonterminal)   
                
                # Return the syntax tree as string representation:          
                return (syntax_tree, tree_probability)
             
        else:
            # Else: The nonterminal in not a start symbol. That means there
            # is no possible parse for the input sentence.
            print "PARSING ERROR: Sentence not in language. \n"
                
#####################################################################
#                            Get Tree                               #
#####################################################################

    # Recursive function that computes a tree for a given nonterminal
    # and its matrix coordinates:        
    def get_tree(self, i, j, symbol):
        
        # Position in matrix:
        matrix_coordinates = self.matrix[i][j]
        
        # Recursive case:
        # If there is not a zero in tuple position two (if there was, it would be a leaf node and the
        # dictionary entry would look like this: ('the', 0, 0, 0.3), therefore we make that distinction)
        if matrix_coordinates[symbol][1] != 0:
        
            # For debugging purposes:
            assert len(matrix_coordinates[symbol]) == 4
                
            nts1 = matrix_coordinates[symbol][0]            # First position: first nonterminal
            nts2 = matrix_coordinates[symbol][1]            # Second position: second nonterminal
            k = matrix_coordinates[symbol][2]               # Third position: Teilungspunkt
            
            # Recursive function call to get both subtrees:
            subtree_1 = self.get_tree(i , k-1, nts1)
            subtree_2 = self.get_tree(i+k, j-k, nts2)
            
            # Return the tree that covers both subtrees:
            return nltk.Tree(symbol, [subtree_1, subtree_2])
        
        else:
            # Base case: Leaf node
            
            # For debugging purposes:
            assert len(matrix_coordinates[symbol]) == 4
            
            # Iterate over matrix cells [i][0] (contain all the input terminal symbols):
            for symbol in self.matrix[i][0]:
                terminal_symbol = matrix_coordinates[symbol][0]
            
            # Return the leaf of the tree:   
            return nltk.Tree(symbol, [terminal_symbol])

            
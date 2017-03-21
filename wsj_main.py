
#####################################################################
##                    Probabilistic CKY Parser                     ## 
##                Main File for Wall Street Journal                ## 
#####################################################################


#####################################################################
# File:                           wsj_main.py                       #
# Author:                         Aline Castendiek                  #
# Student ID:                     768297                            #
# Date:                           30/10/14                          #
# 1st operating system:           Windows 7 [6.1.7601]              #
# 2nd operating system:           Linux Mint 17 Qiana[Ubuntu 14.04] #
#####################################################################

import CKYProbabilisticParser
import sys
import nltk.grammar 

#####################################################################
#              Create Wall Street Journal Grammar                   #
#####################################################################

# Using NLTK internal functions for reading in Wall Street Journal:
def create_wsj_grammar(no_of_sentences):
    nt_counter = dict()          # Dictionary for counting the nonterminals on lhs
    productions = dict()        # Dictionary for counting the occurrence of all productions
    sentences = list()          # List that will contain all the sentences later on
    start_symbol = None         # Set start symbol to None at the beginning
    no_of_all_sentences = 0     # Count of all sentences 

    # Count all the sentences using NLTK internal functions:
    for fileid in nltk.corpus.treebank.fileids():
        for tree in nltk.corpus.treebank.parsed_sents(fileid): 
            no_of_all_sentences += 1

    # If the desired number of sentences given as function argument is larger 
    # than the actual number of sentences, set the actual number as new maximum:
    if no_of_sentences > no_of_all_sentences:
        no_of_sentences = no_of_all_sentences

    # Load Wall Street Journal (has 3914 trees):
    for fileid in nltk.corpus.treebank.fileids():
        for tree in nltk.corpus.treebank.parsed_sents(fileid): 
            # Leave inner for loop if the variable == 0:
            if no_of_sentences == 0:
                break

            else:
                # Count down no_of_sentences variable:
                no_of_sentences -= 1 

                # Join the sentences:
                sentences.append(" ".join(tree.leaves()))

                # Set the start symbol to existing tree node:
                if start_symbol == None:
                    start_symbol = nltk.grammar.Nonterminal(tree.node)

                # Use NLTK CNF conversion:      
                tree.chomsky_normal_form(horzMarkov = 2)  # Convert to CNF
                tree.collapse_unary(collapsePOS = True) # Remove unary rules 

                # Iterate over all rules in the tree:
                for production in tree.productions(): 
                 # Count the lhs: 
                    if production.lhs() in nt_counter:
                        nt_counter[production.lhs()] += 1
                    else:
                        nt_counter[production.lhs()] = 1

                    # Count the rule's occurrence:
                    if production in productions: 
                        productions[production] += 1
                    else:
                        productions[production] = 1

    # Now we create the actual grammar.
    grammar_list = list()

    # Iterate over productions and calculate probability:
    for production in productions:
        probability = productions[production] /  float(nt_counter[production.lhs()]) 

        # Create the new rule:
        prob_rule = nltk.grammar.WeightedProduction(production.lhs(), production.rhs(), prob = probability)

        # Append the new rule to out grammar list:
        grammar_list.append(prob_rule)

    # Return a pair of the grammar and all possible sentences:
    return (nltk.grammar.WeightedGrammar(start_symbol, grammar_list), sentences)


#####################################################################
#                            Main Function                          #
#####################################################################

# Command line arguments: 
# [0]: wsj_main.py
# [1]: number of desired sentences 
# [2]: any chosen output file
if len(sys.argv) == 3:

    # Call function to create a grammar object for any number of sentences:
    wsj_grammar = create_wsj_grammar(int(sys.argv[1]))
    input_sent = wsj_grammar[1]             # Object index 1 contains the input sentences  
    grammar = wsj_grammar[0]                # Object index 0 contains correspondent grammar

    #print grammar
    #print input_sent

    # Set parser to None in the beginning (just in case):
    #parser = None

    # Create parser object for newly created grammar:
    parser = CKYProbabilisticParser.ProbCKYParser(grammar) 

    parse_list = []

    # Split every sentence in input and add it to a list that contains all sentences:
    for sentence in input_sent:
        parse_list.append(sentence.split())

    # Create and open a file:
    output_file = open(sys.argv[2], 'w')
    # Parse every sentence in parse_list and write the result into output file:
    for parse_sentence in parse_list:
        #print "parse_sentence :", parse_sentence
        result = parser.prob_cky_parse(parse_sentence)
        #result[0].draw()
        #print "result: ", result
        #print "Type of result: ", type(result)

        # Formatting results (result[0] is the tree, result[1] is its probability):
        output_file.write("{0} \t {1} \n".format(result[0], result[1]))
    output_file.close()

# Print instructions:
else:
    print "USAGE: wsj_main.py number_of_sentences output_file \n"
    print "number_of_sentences: Desired number of input sentences that should be parsed. \n"
    print "output_file: Choose a file name, that file will be created and contain the result. \n"
    print "IMPORTANT INFORMATION: For the programm to run properly, you will need to download the Wall Street Journal from NLTK. \n"
    print "To obtain the Wall Street Journal, please execute following steps: \n" 
    print "1. Open your python command line. \n"
    print "2. Type 'import nltk' \n"
    print "3. Type 'nltk.download()' \n"
    print "4. The NLTK Downloader will open. Under Corpora, choose the appropriate corpus and click download."

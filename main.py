
#####################################################################
##                    Probabilistic CKY Parser                     ## 
##                          Main File                              ## 
#####################################################################


#####################################################################
# File:                           main.py                           #
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


import CKYProbabilisticParser
import CNFConversion
import sys
import nltk.grammar


#####################################################################
#                 Is in Chomsky Normal Form                         #
#####################################################################

# Bool function. Takes grammar as argument and returns true if it is in Chomsky Normal Form.
def is_in_cnf(grammar):
    for rule in grammar.productions():
        # If not(len = 1 and is terminal) and not(len = 2 and both are nonterminals): 
        if not (len(rule.rhs()) == 1 and nltk.grammar.is_terminal(rule.rhs()[0])) and not (len(rule.rhs()) == 2 and nltk.grammar.is_nonterminal(rule.rhs()[0]) and nltk.grammar.is_nonterminal(rule.rhs()[1])):
            # Return false, because then the grammar is not in Chomsky normal form:
            return False
    # Else it is in CNF, so return true:
    return True    


#####################################################################
#                       Parsing Process                             #
#####################################################################

# Command line arguments: 
# [0]: main.py
# [1]: probabilistic context free grammar
# [2]: file with input sentences
# [3]: output file 
if len(sys.argv) == 4:
    
    # Read in grammar from command line:
    filepath = "file:{0}".format(sys.argv[1])

    grammar = nltk.data.load(filepath, 'pcfg')
    parser = None
    
    # If the grammar is not in CNF, we want to create a CNF-Conversion object:
    if not is_in_cnf(grammar):
        cnf_instance = CNFConversion.CNF_Conversion(grammar)
        # Get grammar and save it:
        cnf_converted_gram = cnf_instance.get_grammar()
        
        # Create parser object for newly converted gram:
        parser = CKYProbabilisticParser.ProbCKYParser(cnf_converted_gram)
        
    else:
        # Else create the parser using the original grammar:
        parser = CKYProbabilisticParser.ProbCKYParser(grammar) 
    
    # Open and read input file:
    input_file = open(sys.argv[2], 'r')
    parse_list = []
    # Split every sentence in input and add it to a list that contains all sentences:
    for sentence in input_file:
        parse_list.append(sentence.split())
    
    # Create and open the file that will contain the results:
    output_file = open(sys.argv[3], 'w')
    # Parse every sentence in parse_list and write the result into output file:
    for parse_sentence in parse_list:
        # print "Parse_sentence :", parse_sentence
        result = parser.prob_cky_parse(parse_sentence)
        #print "Result: ", result
        output_file.write("{0} \t {1} \n".format(result[0], result[1]))
        
    output_file.close()


#####################################################################
#                       Print Instructions                          #
#####################################################################

else:  
    print "USAGE FOR PARSING: "     
    print "python main.py pcfg input_file output_file \n"
    print "pcfg = A probabilistic context free grammar. All rules have to be of this form: nonterminal -> symbols [float value], "
    print "so that they have exactly one nonterminal symbol on the left hand side and at least one symbol on the right hand side. "
    print "Terminal symbols must be represented with single quotation marks. The probability value of the rule must be written " 
    print "in square brackets. Any additional characters might cause problems for NLTK. \n"
    print               "input_file = File to be parsed that contains one sentence per line. Words will be tokenized by spaces. \n"
    print               "output_file = File in which the trees and their probabilities will be written. \n"
    
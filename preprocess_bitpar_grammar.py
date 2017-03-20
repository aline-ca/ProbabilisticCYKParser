
#####################################################################
##                    Probabilistic CKY Parser                     ## 
##                    Preprocess BitPar Grammar                    ## 
#####################################################################


#####################################################################
# File:                           preprocess_bitpar_grammar.py      #
# Author:                         Aline Castendiek                  #
# Student ID:                     768297                            #
# Date:                           30/10/14                          #
# 1st operating system:           Windows 7 [6.1.7601]              #
# 2nd operating system:           Linux Mint 17 Qiana[Ubuntu 14.04] #
#####################################################################

import sys
import nltk.grammar

#####################################################################
#                     Find Symbols Top Down                         #
#####################################################################

# Recursive function for removing underivable rules. Takes three arguments:
# The first symbol on the lhs, our dictionary of rules (maps a nonterminal 
# to a list of all rules it creates) and a list of all found symbols.
def find_symbols_top_down(symbol, rules, foundSymbols):
	# For every rule that has the symbol on the lhs:
	for rule in rules[symbol]:
		# For every symbol that is on the rule's rhs:
		for new_symbol in rule.rhs():
			# If this new symbol is not yet in our found_symbols list, but it is in rules:
			if new_symbol not in found_symbols and new_symbol in rules:
				# Append the new symbol to our found_symbols list:
				found_symbols.append(new_symbol)
				# Call same function recursively, but this time with the new symbol as the first symbol: 
				find_symbols_top_down(new_symbol, rules, found_symbols)


#####################################################################
#                    	   Main Script     		                    #
#####################################################################

# Command line arguments: 
# [0]: preprocess_bitpar_grammar.py
# [1]: grammar file
# [2]: lexicon file
# [3]: threshold value
# [4]: output file 
if len(sys.argv) == 5:

	grammar_file = open(sys.argv[1], 'r')
	lexicon_file = open(sys.argv[2], 'r')
	threshold_value = sys.argv[3]

	# Maps a lhs to a list of all rules it creates:
	lhs_to_rules = dict() 

	# Set start symbol to None at the beginning:
	start_symbol = None

	# Another dictionary that saves all the created rules and their frequency
	# (necessary for calculating the probability):
	lhs_to_rule_frequency_list = dict()

	# For all lines in file (each line is a rule):
	for line in grammar_file:
		# Tokenize each line:
		tokens = line.split()

		# Has to contain at least the frequency, one lhs and one rhs symbol: 
		assert len(tokens) > 2

		frequency = tokens[0]

		# Only use rules that have a frequency that is larger than the threshold value:
		if frequency > threshold_value:
			lhs_nt = nltk.grammar.Nonterminal(tokens[1])

			# This list will contain all the symbols on the rhs:
			rhs_list = list()

			# Iterate over all symbols on the rhs and append them to rhs_list
			# as NLTK nonterminals:
			for i in range(2, len(tokens)):
				rhs_list.append(nltk.grammar.Nonterminal(tokens[i]))

			# Set the start symbol to the first lhs nonterminal:
			if start_symbol is None: 
				start_symbol = lhs_nt

			# Create the actual rule:
			rule = nltk.grammar.Production(lhs_nt, rhs_list)

			# Append the new rule and its frequency to the dictionary:
			if lhs_nt in lhs_to_rule_frequency_list:
				lhs_to_rule_frequency_list[lhs_nt].append((rule, frequency))
			else:
				lhs_to_rule_frequency_list[lhs_nt] = [(rule, frequency)]

	# Now that we have the NLTK rules and their frequencies, 
	# we want to calculate the probability of them.

	# To do so, we first count all rules to find the denominator for our calculation.
	
	# For all lhs symbols in the dictionary:
	for lhs in lhs_to_rule_frequency_list:
		
		score = 0
		for rule, frequency in lhs_to_rule_frequency_list[lhs]:
			score += int(frequency)

		# Convert the score to int:
		complete_frequency = float(score)

		# Now that we know the overall frequency as well as the frequency of all rules,
		# we can calculate the probability and create the new rule:
		for rule, frequency in lhs_to_rule_frequency_list[lhs]:
			new_rule = nltk.grammar.WeightedProduction(rule.lhs(), rule.rhs(), prob=(int(frequency) / complete_frequency))
				
			# Then we add the new rule to the lhs_to_rules dictionary:
			if new_rule.lhs() in lhs_to_rules:
				lhs_to_rules[new_rule.lhs()].append(new_rule)
			else:
				lhs_to_rules[new_rule.lhs()] = [new_rule]

	# BitPar stores nonterminal rules and production rules in two different files.
	# Now we read in the lexicon file as well and process it pretty similar to 
	# what we did with the grammar file before.
	
	# Dictionary that maps a nonterminal (PoS-tag) to a list of terminal symbols
	# and their frequency: 
	pos_to_word_frequency = dict()

	# Read in and tokenize lexicon:
	for line in lexicon_file:
		tokens = line.split()

		# len of tokens has to be at least three (lhs, rhs and frequency)
		assert len(tokens) >= 3
		
		# The terminal symbol is the very first token of every rule: 
		terminal = tokens[0]

		# We will use last_pos to store the current PoS tag. Set it to None:
		last_pos = None

		# For all positions in tokens: 
		for i in range(1, len(tokens)):
			
			# If last_pos is None, set it to the current token as NLTK nonterminal:
			if last_pos == None:
				last_pos = nltk.grammar.Nonterminal(tokens[i])
			
			# Else: If last_pos has been set to the nonterminal, we can create
			# a matching pair of terminal and frequency (tokens[i]) for it.      
			else:
				new_pair = (terminal, int(tokens[i]))

				# Now we append our new pair to the pos_to_word_frequency 
				# dictionary at the index of our last_pos tag:  
				if last_pos in pos_to_word_frequency:
					pos_to_word_frequency[last_pos].append(new_pair)
				else:
					pos_to_word_frequency[last_pos] = [new_pair]

				# After creating the new pair, set last_pos back to None:
				last_pos = None

		# Similar to what we did before with the grammar, we now count the overall 
		# occurrence of a PoS tag to get the denominator for our probability calculation.       

	# Iterate over all PoS tags in our dictionary:
	for pos in pos_to_word_frequency:
		score = 0
		
		for terminal, frequency in pos_to_word_frequency[pos]:
			score += int(frequency)

		# Convert the overall count of a PoS tag to float:
		overall_count = float(score)
		
		# Now that we know the overall count of every PoS tag, we can create new 
		# NLTK rules by iterating over all terminal symbols that can be derived
		# from this particular PoS tag. To get the probability, we simply divide
		# the terminal's frequency by the overall frequency of the PoS tag.    
		
		for terminal, frequency in pos_to_word_frequency[pos]:
			rule = nltk.grammar.WeightedProduction(pos, [terminal], prob=int(frequency) / overall_count)
			
			# lhs_to_rules is the dictionary that is supposed to store all the 
			# rules (defined in the beginning). We already added the production
			# rules before, so we can now append the lexicon rules as well:  	
			if rule.lhs() in lhs_to_rules:
				lhs_to_rules[rule.lhs()].append(rule)
			else:
				lhs_to_rules[rule.lhs()] = [rule]

	# Now we have all the rules that we wanted. But since we did not use all the 
	# rules from the grammar but only the ones that have a high enough frequency, 
	# we also have a lot of rules now that cannot be derived from the start symbol.
	# To get rid of those rules, we use the recursive find_symbols_top_down function.
	
	found_symbols = list()
	# This function 
	find_symbols_top_down(start_symbol, lhs_to_rules, found_symbols)

	# new_rules will be our new list of rules that only contains the derivable ones: 
	new_rules = list()

	# Iterate over all derivable symbols and all rules that have this symbol on 
	# their lhs, then append the rules to our new_rules list:
	for derivable_symbol in found_symbols:
		for rule in lhs_to_rules[derivable_symbol]:
			new_rules.append(rule)


#####################################################################
#         Create the grammar and write it into Output File     		#
#####################################################################
	
	# Create NLTK grammar object:
	grammar = nltk.grammar.WeightedGrammar(start_symbol, new_rules)

	# Open output file. First, write all the rules in it that can be 
	# derived from the start symbol.  
	output_file = open(sys.argv[4], 'w')
	for rule in lhs_to_rules[start_symbol]:
		output_file.write(str(rule) + "\n")
	
	# Then, write all the other rules in it.	
	for symbol in found_symbols:
		if symbol != start_symbol:
			for rule in lhs_to_rules[symbol]:
				output_file.write(str(rule) + "\n")

	output_file.close()


#####################################################################
#                      Print Instructions     		                #
#####################################################################

else:
	print "USAGE FOR CONVERTING BITPAR GRAMMAR TO NLTK PARSABLE GRAMMAR: " 
	print "python prepocess_bitpar_grammar.py grammar_file lexicon_file threshold_value output_file"
	print               "grammar_file = BitPar grammar file"
	print               "lexicon_file = BitPar lexicon file"
	print               "threshold_value = Frequency value. All rules with a frequency below the threshold will be ignored."
	print               "output_file = File in which the new grammar will be written \n"


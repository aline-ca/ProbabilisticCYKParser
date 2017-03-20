
#####################################################################
##                    Probabilistic CKY Parser                     ##
##              Convert to Chomsky Normal Form Class               ##
#####################################################################


#####################################################################
# File:                           CNFConversion.py                  #
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

# Converts a given grammar to Chomsky Normal Form so that there are only 
# productions of the form A -> BC or A -> 'a'. All necessary conversion functions
# get called inside the constructor.
class CNF_Conversion(object):

    def __init__(self, start_grammar):

        # Original grammar that is to be converted:
        self.start_grammar = start_grammar

        # Separated grammar:
        self.separated_gram = self.separate_grammar(start_grammar)

        # Grammar after removing all unit rules:
        self.unit_rule_free_gram = self.remove_all_unit_rules(self.separated_gram)

        # Global variables that are necessary for creating new nonterminals
        # (required for binarization):
        self.var_counter = 1
        self.var = "X"
        
        # Binarized grammar:
        self.binarized_gram = self.binarize(self.unit_rule_free_gram)
        

#####################################################################
#                       Separate Grammar                            #
#####################################################################

    # Separates grammar so that there are either only nonterminals
    # or only terminals on the right hand side of the production.
    def separate_grammar(self, grammar):

        # List that will contain all the newly created grammar rules as tuples
        # (return value of function)
        tuple_grammar_list = []

        # Create the mapping of terminal to nonterminal symbols:
        rule_dictionary = self.create_sep_dict(grammar)

        for rule in grammar.productions():
            # order_list saves the nonterminal symbol lists in proper order:
            order_list = []

            # If there are at least two symbols on the right hand side of the production:
            # We want to ignore unary rules for two reasons here:
            # 1. We do not want unit rules (there is a special function for removing them)
            # 2. We do not want the unary lexical rules (no need to change them, they are already in CNF)
            if len(rule.rhs()) > 1:

                for symbol in rule.rhs():
                    # List of all nonterminal symbols that could replace the current symbol:
                    nt_symbols_list = []

                    # If the current symbol is a terminal symbol:
                    if nltk.grammar.is_terminal(symbol):

                        # Get the matching nonterminal for this terminal symbol from the rule dictionary
                        # and store it in the nonterminal symbol list:
                        nt_symbols_list = self.get_nonterminal(symbol, rule_dictionary)

                    # If the current symbol is a nonterminal symbol:
                    else:
                        # Store this current nonterminal symbol in a list:
                        nt_symbols_list = [symbol]

                    # Append the current nonterminal list to the order list:
                    order_list.append(nt_symbols_list)

                # The newly created order list (one list for each rule) has to have
                # just as many positions as the rhs of the production:
                assert len(order_list) == len(rule.rhs())

                # To get all possible nonterminal combinations, we need to compute 
                # the cartesian product of all the nonterminal symbols stored in order_list:
                all_rhs = self.cart_prod(order_list)

                # Append all those rules to a new list:
                all_rhs_list = []
                for prod in all_rhs:
                    all_rhs_list.append(prod)

                for new_rhs in all_rhs_list:
                # Create the new rule: a triple consisting of the original left hand 
                # side of the production, the new right hand side and the probability 
                # of the old rule divided by the number of total rules for this nonterminal symbol
                    new_rule = (rule.lhs(), new_rhs, rule.prob()/len(all_rhs_list))
                    tuple_grammar_list.append(new_rule)
                    
        # Convert the new rules from tuples to NLTK objects:
        list_gram = self.get_str_rep(tuple_grammar_list)

        # Append all old unary rules to the new grammar list as well:
        for rule in grammar.productions():
            if len(rule.rhs()) < 2:
                list_gram.append(rule)

        # Create NLTK grammar instance from list:
        return nltk.grammar.WeightedGrammar(grammar.start(), list_gram)


#####################################################################
#                       Get Cartesian Product                       #
#####################################################################

    # Compute all cartesian products of a list.
    # (for further details see list of references in Dokumentation.pdf)   
    def cart_prod(self,lists, previous_elements = []):
        if len(lists) == 1:
            for elem in lists[0]:
                yield previous_elements + [elem, ]
        else:
            for elem in lists[0]:
                for x in self.cart_prod(lists[1:], previous_elements + [elem, ]):
                    yield x


#####################################################################
#                    Get String Representation                      #
#####################################################################

    # Transforms the list of generated grammar rules into a NLTK compatible string representation.
    def get_str_rep(self, gram_rules):

        gram_list = []

        # For every rule in list:
        for rule_tuple in gram_rules:
            rule = nltk.grammar.WeightedProduction(rule_tuple[0], rule_tuple[1], prob=rule_tuple[2])
            gram_list.append(rule)

        return gram_list


#####################################################################
#                     Remove All Unit Rules                         #
#####################################################################

    # Function that iterates over all grammar rules, checks whether the grammar 
    # contains unit rules and if it does, calls the remove_unit_rule function (defined below):
    def remove_all_unit_rules(self, grammar):

        # List that will contain the newly created rules later on:
        new_rule_list = []
        # List that will contain all the other rules from the grammar that we want to keep:
        remaining_rules = []

        # For every production in grammar:
        for production in grammar.productions():

            # If the length of the rhs of the production is 1 and is a nonterminal
            # (therefore it has to be a unit rule):
            if len(production.rhs()) == 1 & nltk.grammar.is_nonterminal(production.rhs()[0]) :

                list_of_rules = [production]

                # Empty set that will be filled later on and used to
                # check whether a nonterminal symbol has already been visited:
                visited = set()

                # Call the remove unit rule function for every unit rule in the grammar:
                self.remove_unit_rule(production, list_of_rules, new_rule_list, visited)
            else:
                remaining_rules.append(production) 
        
        # Append the remaining rules from the original grammar:
        new_rule_list = new_rule_list + remaining_rules    
                
        # Create nltk grammar instance from list:
        new_gram = nltk.grammar.WeightedGrammar(grammar.start(), new_rule_list)
        return new_gram
    

#####################################################################
#                         Remove Unit Rule                          #
#####################################################################

    # Function for removing a unit rule (gets called in remove_all_unit_rules).
    # Takes four arguments:

    # 1. rule = the unit rule

    # 2. list_of_rules = a list that will append all unit rules that can be derived
    # from another unit rule in corresponding order until a lexical rule is reached.
    # e.g.: [S -> X, X -> Y, Y -> Z, Z -> 'z']

    # 3. new_rule_list = a list that will contain all the newly created rules for
    # this one particular chain of consecutive unit rules.

    # 4. visited = a set that will help to recognize cycles in the rules that could
    # go on recursively (eg. A -> B, B -> A). If we ignored those cycles the program
    # would try to continue building the list_of_rules indefinitely and would eventually crash.

    def remove_unit_rule(self, rule, list_of_rules, new_rule_list, visited):

        # Create unit rule dictionary:
        unit_rule_dict = self.create_unit_rule_dict()

        # First symbol on the rhs:
        first_rhs_sym = rule.rhs()[0]

        # Only execute following steps if the nonterminal rule on lhs is not yet contained in the visited set:
        if rule.lhs() not in visited:

            # Add the current rule to the visited set to prevent cycles:
            visited.add(rule.lhs())

            # Recursive case:
            # if the rhs of a rule consists of exactly one nonterminal symbol
            # (because then it is a unit rule):
            if len(rule.rhs()) == 1 & nltk.grammar.is_nonterminal(first_rhs_sym):


                # For every value in the unit_rule_dictionary that has the first_rhs_sym as key:
                for next_rule in unit_rule_dict[first_rhs_sym]:

                    # Create a copy of list_of_rules:
                    new_list_of_rule = list(list_of_rules)

                    # Append rule from the dictionary to the list:
                    new_list_of_rule.append(next_rule)

                    # Now call same function recursively with following arguments:
                    # the next rule in the dictionary as next_rule, the newly created copy
                    # of the rule list as new_list_of_rule, the newly created rule list as
                    # new_rule_list and a copy of the visited set as set(visited).
                    self.remove_unit_rule(next_rule,new_list_of_rule, new_rule_list, set(visited))

            else:
                # Base case: The rule is a lexical rule.
                # Here we generate the new grammar rules for every chain of unit rule productions.
                # e.g. when we have [S -> N, N -> B, B -> 'b'] as list_of_rules,
                # we need to create the rule S -> 'b', but NOT N -> 'b' because we will also
                # have a list of rules [N -> B, B -> 'b'], therefore this new rule will be
                # taken care of separately.

                # new lhs of the new rule will be the lhs symbol of the first list_of_rules element:
                new_rule_lhs = list_of_rules[0].lhs()
                # new rhs of the new rule will be the rhs symbol (which is a terminal) of the current rule:
                new_rule_rhs = rule.rhs()
                # new probability of the rule, initial value is 1 since that is the identity element for multiplication:
                new_probability = 1

                # For every element(rule) in list_of_rules:
                for entry in list_of_rules:
                    # new probability is the new probability times the rule's original probability:
                    new_probability *= entry.prob()

                # Create a new NLTK rule:
                new_rule = nltk.grammar.WeightedProduction(new_rule_lhs, new_rule_rhs,  prob=new_probability)

                # Store the newly created rule in the new_rule_list:
                new_rule_list.append(new_rule)


#####################################################################
#                         Binarize Grammar                          #
#####################################################################
    
    # The binarize function takes a grammar as argument and returns a binarized
    # grammar. The binarization will happen as follows: We will create a list 
    # that contains all nonterminals of the rhs of the rule and continue to create
    # new rules with new nonterminals for its elements until there are only two
    # elements left.
    # e.g.: If we have a rule (S -> A B C D E), we will create the new rules in 
    # following manner: (S -> A X1), (X1 -> B X2), (X2 -> C X3), (X3 -> D E) 
    
    def binarize(self, grammar):
        
        # gram_rules_list will contain all newly created rules and
        # all old rules from the original grammar that we want to keep:    
        gram_rules_list = []
        
        for rule in grammar.productions():

            # If the length of the right hand side of the rule is at least 3:
            if len(rule.rhs()) > 2:

                # Create list copy of the rhs of the rule:
                rhs_list = list(rule.rhs())

                # Prob of the first rule to be created is the current rule's prob:
                next_prob = rule.prob()

                # The next lhs of the new rule will be the current rule's lhs:
                next_lhs = rule.lhs()

                # While the length of the right hand side of the rule is at least three:
                while len(rhs_list) > 2:
                    
                    # Call get_next_variable function to generate a new nonterminal:
                    v = self.get_next_variable()

                    # The new rule will have next_lhs as lhs. On the rhs will be a
                    # tuple consisting of the first element of rhs_list and the new nonterminal:
                    new_rule = nltk.grammar.WeightedProduction(next_lhs, (rhs_list[0], v), prob=float(next_prob))
                    gram_rules_list.append(new_rule)

                    # next_lhs for the next new rule will be the new nonterminal:
                    next_lhs = v
                    # Pop leftmost element from rhs_list (position [0]):
                    rhs_list.pop(0)

                    # Since we now create rules for completely new nonterminals, the probability will always be 1:
                    next_prob = 1

                    # If the length of the right hand side of the rule is exactly two:
                    if len(rhs_list) == 2:
                        # We do not need to generate another nonterminal - instead we use
                        # the two last elements (nonterminals) of the rhs_list and add them to
                        # the new rhs of the new rule:
                        new_rule = nltk.grammar.WeightedProduction(next_lhs, (rhs_list[0], rhs_list[1]), prob=float(1.0))
                        gram_rules_list.append(new_rule)
        
        # Append all original grammar rules that have a rhs that is smaller than 3 to the list:
        for rule in grammar.productions():
            if len(rule.rhs()) < 3:
                gram_rules_list.append(rule)

        # Create NLTK grammar instance from list:
        return nltk.grammar.WeightedGrammar(grammar.start(), gram_rules_list)
    

#####################################################################
#                         Get Next Variable                         #
#####################################################################

    # Function that is called inside the binarize function.
    # During binarization there is the need for new nonterminal symbols that
    # can be used to split the rules. get_next_variable creates a new variable
    # using var_counter which is declared within the constructor - this way new
    # variables named X1, X2, X3 etc will be created.

    def get_next_variable(self):

        # the new variable, has to be of nltk nonterminal type:
        new_var = nltk.grammar.Nonterminal(self.var + str(self.var_counter))
        
        # increase var_counter by one after generating a new variable:
        self.var_counter += 1

        return new_var


#####################################################################
#                   Create Separation Dictionary                    #
#####################################################################

    # Creates a dictionary that maps a terminal symbol (key) to a list of corresponding nonterminals (values):
    def create_sep_dict(self, gram_to_be_mapped):

        rule_dict = {}

        # for every rule in productions:
        for rule in gram_to_be_mapped.productions():

            # for every terminal symbol on rhs:
            for term_symb in rule.rhs():
                if nltk.grammar.is_terminal(term_symb):

            # if it is a lexical rule:
                    if len(rule.rhs()) == 1:

                        if term_symb not in rule_dict:
                            rule_dict[term_symb] = [rule.lhs()]

                        # if the terminal is already in the dictionary:
                        else:
                            # append the new nonterminal:
                            rule_dict[term_symb].append(rule.lhs())
        return rule_dict


#####################################################################
#                    Create Unit Rule Dictionary                    #
#####################################################################

    # Creates a dictionary that maps a nonterminal symbol (key) to a list
    # of all rules that have the nonterminal on its left hand side (value):
    def create_unit_rule_dict(self):

        rule_dict = {}

        # For every rule in productions:
        for rule in self.separated_gram.productions():
            symbol = rule.lhs()

            # If there is no dictionary entry yet:
            if symbol not in rule_dict:
                # Add the complete rule:
                rule_dict[symbol] = [rule]

            else:
                # Else append the rule:
                rule_dict[symbol].append(rule)

        return rule_dict


#####################################################################
#                          Get Nonterminal                          #
#####################################################################

    # Function for getting the corresponding nonterminal for a terminal by looking it up in the dictionary:
    def get_nonterminal(self, terminal, rule_dict):
        return rule_dict[terminal]
    
    
#####################################################################
#                          Get Grammar                              #
#####################################################################

    # Function necessary for obtaining grammar inside the main function: 
    def get_grammar(self):
        # Returns the final grammar (binarized). At this point all necessary 
        # function calls for converting already happened inside the constructor.
        return self.binarized_gram



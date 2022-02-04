

# -*- coding: utf-8 -*-
"""
voir __pt_facteur_unique
pre-recherche des termes supplémentaire avant petrik
"""
"""
   Complete minimization of logical functions to large number of variables.
   Quick, simple method, providing all solutions in the form of reduced minterms.
   This method has nothing to do with the Quine-McClusKey method.
   Its principle is to reduce each minterm individually so that its coverage does not meet maxterms
   (I have done tests with more than 25 variables).
   The solution includes:
   -the essential reduced minterms
   -The additional reduced minternes for a complete coverage
   -the synthesis where we find all the choices in the reduced minterms for a complete coverage.
   The method is based on an algorithm I’ve been using since 1966.
   In 1970, I built on this algorithm, a relay machine that made it possible to simplify the terms of 5 variables
   (I still have his plans).
   In 1974, a first program in Fortan (about 300 cards) which allowed me to move to terms with 10 variables
   In 1980, a basic program on a PC heatkit H8 with a 16K RAM allowed to simplify always 10 variables.
   Finally, in 2021, I took exactly the same alogithme to make one
"""
__author__ = 'Yvon Martin'
__version__ = "0.2"
__author_email__ = 'yvon.l.martin@gmail.com'



def decode_bin(tup_terme, size):
    """
    decode the tupple (terme, masque) to make a string
    readable by 0,1, -
    for example (9, 4)  gives 1-01&
    """
    terme, msq = tup_terme
    return "".join(['-' if msq & (1 << k) else '1' if terme & (1 << k )
                else '0' for k in range(size-1, -1, -1)])

"""-------------------------------------------"""

def edit_solution(terme01, nom_variable):
    """
    Passes from a term represented as for example 1-0- to
    the AC' form (for a term with 4 ABCD variables)
    """
    return "".join([''if i == '-' else j if i == '1' else j+"'" if i == '0'else ''
                for(i ,j) in zip(terme01,nom_variable)])
"""-------------------------------------------"""
def acqui_terme(chaine01, size):
    """
    Transforms into tuple (term, mask) an entry of type for example '01-10-' -> (20, 9)
    """
    erreur = False
    nbr= len(chaine01)
    terme, msq = 0, 0
    msq = 0
    if size != nbr:
        erreur = True
        return (terme, msq), erreur
    pt = 1 << size
    for i in chaine01:
        pt >>= 1
        if i == "1":
            terme += pt
        elif i == "-":
            msq += pt
        elif i != "0":
            erreur = True
            terme, msq = 0, 0
            break
    return (terme, msq), erreur

"""----------------------------------------------"""
def input_tables_01(data_in, size):
    """
    Decode the stack (alphabetical list of 3 characters '1-0') data_in to form
    the standardized list(s) of terms 1 and 0. Each element is a
    tuple (term, mask). the hidden bits of the term are normalized to 0
    """
    terme_0 = set()
    terme_1 = set()
    erreur = False
    # par défaut on commence à lire les termes 1
    type_terme = 1
    while len(data_in) != 0:
        rep = data_in.pop()
        if rep == "t1":
            type_terme = 1
        elif rep == "t0":
            type_terme = 0
        else:
            terme, erreur = acqui_terme(rep, size)
            if erreur:
                terme_0 = set()
                terme_1 = set()
                break
            if type_terme == 0:
                terme_0.add(terme)
            else:
                terme_1.add(terme)
    return (list(terme_1), list(terme_0), erreur)  # liste normalisée

"""================= classe ================================="""
class Simply:
    """
    calculates all reduced optimal terms from terms 1 and terms 0
    Instanciation of the class
    	args:
            number of variables in a term
            options list [v,.,....]
                v : verbose mode
			
    use of the class	
        args:
            table_1  terms list (list of tuple) that describe when the output function is one.
                e.g. [[(t1, m1),(t2, m2)....] (tuple : term t with this mask m)
            table_2 idem, terms list that describe when the output function is zero.


    return:
        Complete solutions in the form of a list of 3 sub-lists
        -essential terms in the first sub-list
        -additional terms in the second sub-list
         each simplified term is represented by a tuple (term, mask)
         e.g. (20, 9) is the simplified term 1-10-

        -synthesis: solutions to cover minterms in the third sub-list
        e.g. [[(t1, m1),(t2, m2)] [(t1, m1),(t2, m2)(t3, m3),(t4, m4] [(2)(1, 3),(1,4)]
        2 essential terms, 4 additional terms, choose from the
        additional 2 (best solution) or 1 and 3 or 1 and 4
    """
    """==========================================================================="""

    #Initialize an instance with the number of variables of the function
    def __init__(self, size, **arg_list ):
        self.SIZE = size
        self.arg_list = arg_list
        self.MSQ1000B = 1 << self.SIZE
        self.MSQ0111B = (1 << self.SIZE)- 1



    # Call of the instance with the binary tables of the minterms and Max terms as parameter
    def __call__(self, tbl_1, tbl_0):
        self.tbl_1 = tbl_1
        self.tbl_0 = tbl_0     #list_normalise

        def __expense(terme_0_1):
            """
            Produces the  (set) list of binary numbers corresponding to the
            normalized terms: tupple list (term, mask)
            example tupple (2, 5) (the term 1 '0-1-') returns the expension
            '0001', '0011', '1001', '1011' or cover in set {1, 3, 9,11}
           """
            terme_expense = set()
            for i in terme_0_1:
                terme, masque = i
                table_ptr = [pt for pt in [1 << i for i in range(0, self.SIZE)] if (masque & pt)]
                lp = len(table_ptr)
                l1 = 1 << lp
                for pt_terme in range(l1):
                    tr = terme & ~masque
                    k = 1
                    for p in range(lp):
                        if pt_terme & k :
                            tr |= table_ptr[p]
                        k <<= 1
                    terme_expense.add(tr)
            return terme_expense

        def __expense_0_1(term_1, term_0):
            """
            From the normalized list, returns the binary lists of terms 1
            followed by the list of terms 0 followed by an error flag
            """
            erreur = False
            if len(term_0) == 0:
                term1 = __expense(term_1)
                term0 = set(range(0, self.MSQ1000B)) - term1
            elif len(term_1) == 0:
                term0 = __expense(term_0)
                term1 = set(range(0, self.MSQ1000B)) - term0
            else:
                term1 = __expense(term_1)
                term0 = __expense(term_0)
                if len(set(term1).intersection(set(term0))):
                    erreur = True
                    term1, term0 = set(), set()
            return list(term1), list(term0), erreur

        """--------------------------------------------------------"""
        def __pt_facteur_unique(terme, table_0):
            # retourne un terme reduit dont les bits à 1 pointe les colonnes de facteur essentiel

            pt_terme_unique = 0
            for i in table_0:
                for pt_crx in (1 << x for x in range(self.SIZE)): # 11/10/21
                    if pt_crx == (i ^ terme):
                        pt_terme_unique += pt_crx
                        break
            return pt_terme_unique

        """================== essential terms ========================"""
        def __terme_essentiel(table_1, table_0):
            """
            Discovery of essential terms.
            From the lists of binary terms table_1 and table_0, returns the
            essential terms and the list of terms 1 not covered remaining
            """
            table_essentiel = []
            for tb1 in table_1:
                if (tb1 & self.MSQ1000B) == 0:
                    pt_unique = __pt_facteur_unique(tb1, table_0)
                    fl = 0
                    for i in table_0:
                        if((i ^ tb1) & pt_unique) == 0:
                            fl = 1
                            break
                    if fl == 0:
                        # it is a reduced term
                        table_essentiel.append((tb1 & pt_unique, pt_unique ^ self.MSQ0111B))
                        for index, j in enumerate(table_1):
                            if (tb1 & pt_unique) == (j & pt_unique):
                                table_1[index] |= self.MSQ1000B
            table_1_restant = [i for i in table_1 if (i & self.MSQ1000B) == 0]
            return table_essentiel, table_1_restant


        """=================== additional terms =========================
        args:
            pt_croix : correspond au variables essentielles communes aux differents termes
            table_0_reduit_croix: table des croix reduite (sans les variables essentielles)
        return:
            masque_tr_reduit: liste des masques correspondant à toute solutions possibles

        """
        def __terme_supp(pt_croix, table_0_reduit_croix):
            
            msq = self.MSQ0111B ^ pt_croix
            #msq1 = msq0 - 1
            #s0 = [[]]
            #for croix in table_0_reduit_croix:
            #   s0.append([cpt+1 for cpt in range(self.SIZE) if (croix & msq & (1<<cpt))])
            s0=[[cpt+1 for cpt in range(self.SIZE) if (croix & msq & (1<<cpt))] for croix in table_0_reduit_croix]    
            
            s0=__petrick(s0,PRE_ACCEL)
                

            masque_tr_reduit = []
            for tdim in s0:
                ms = pt_croix
                for i in tdim:
                    ms |= 1 << (i - 1)
                masque_tr_reduit.append(ms)
            return masque_tr_reduit       
        
  

        """================== additional terms ========================= """
        def __termes_supplementaires(table_1_reduit, table_0):
            """
            Discovery of additional terms.
            From the remaining lists of binary terms 1 (not yet covered by essential terms),
            and binary terms 0, returns the list of additional terms allowing
            full coverage of the function
            Si SIM == True, tout les termes supplémentaires  (temps long) seront découvert.
            Si SIM == False, seul le terme couvrant le maximum de termes 1 est retenu 
            et les mintermes couvert sont retirés de la liste des mintermes restant à simplifier.
            Ce mode est tres rapide mais  heuristique . Donc la solution pas nécessairement 
            la meilleure
            """
            if not(DETAIL):
                if len(table_1_reduit):
                    x=table_1_reduit.pop(0)
                    table_1_reduit.append(x)
                
                table_terme_supl = []
                for tab in table_1_reduit:
                    if not(tab & self.MSQ1000B):
                        # Calculer dans pt_croix les variables obligatoires à partir des croix uniques
                        pt_croix = __pt_facteur_unique(tab, table_0)
                        # creer la table des croix hors croix unique ( if not ...)
                        table_0_reduit_croix = [i ^ tab for i in table_0 if not((i ^ tab) & pt_croix)]
                        # chercher toutes les solutions sous forme de masque sur le terme à réduire
                        masque_tr_reduit = __terme_supp(pt_croix, table_0_reduit_croix)
                        priorite = []
                        # print('kk',table_1_reduit, masque_tr_reduit,tab)
                        for msq in masque_tr_reduit:
                            if not(msq & self.MSQ1000B):
                                pr= 0
                                for tr in (table_1_reduit):
                                    if ((tr & self.MSQ1000B)==0 ) and (msq & tab) == (msq & tr ):
                                        pr += 1
                            priorite.append(pr)
                        # terme ayant la plus grande couverture:
                        index_max= max(range(len(priorite)), key=priorite.__getitem__)
                        masq =  masque_tr_reduit[index_max]
                        # retirer les mintermes 1 couverts de la liste des termes 1 restant à simplifier
                        ter = tab,masq ^ self.MSQ0111B
                        for index,tr in enumerate(table_1_reduit):
                            if (masq & tab) == (masq & tr ):
                                table_1_reduit[index] |= self.MSQ1000B
                        table_terme_supl.append(ter)
                        
                t = []
                for (t1,m1) in table_terme_supl:
                    fg= False
                    for (t2,m2) in t:
                        if m1 == m2 and ((t1 | m1 ) == (t2 |m2)):
                            fg = True
                            break
                    if fg == False:
                        t. append((t1,m1))
                return t
                           
            else: 
                """
                Returne toutes les solutions possibles restantes
                """                          
                table_terme_supl = []
                for tab in table_1_reduit:
                    # Calculer dans pt_croix les variables obligatoires à partir des croix uniques
                    pt_croix = __pt_facteur_unique(tab, table_0)
                    # creer la table des croix hors croix unique ( if not ...)
                    table_0_reduit_croix = [i ^ tab for i in table_0 if not((i ^ tab) & pt_croix)]
                    # chercher toutes les solutions sous forme de masque sur le terme à réduire
                    masque_tr_reduit = __terme_supp(pt_croix, table_0_reduit_croix)
                    ter = tab, masque_tr_reduit
                    table_terme_supl.append(ter)
                return list(set( [(term & msq, msq ^ self.MSQ0111B)
                            for (term, t_msq )in table_terme_supl  for msq in t_msq]))
            

        """ ======================= summary table ============================"""
        def __tbl_synthese(table_1_restant, table_terme_supl):
            """
            construction of the summary table to calculate additional terms
            that provide total coverag
            return in DIMACS format with purs literals
            """

            table_synthese = [[] for i in range(len(table_1_restant))]

            cpt = 0
            for ter1, msq in table_terme_supl:
                for index, ter in enumerate(table_1_restant):
                    msq0 = msq ^ self.MSQ0111B
                    if (ter1 & msq0) == (ter & msq0):
                        table_synthese[index].append(cpt + 1)
                cpt += 1
            return table_synthese, cpt

        """=======2e methode ===== list of choices =========================== """
        
        def __petrick(table, acceleration):
            if VERB:
                print('/', end="")
            
            prereduction = []
            #présimplification avant de passer à la méthode Petrick
            # compter dans liste priorite le nombre de croix dans chaque colonnes
            # (sauf dans les colonnes pointées par pt_croix)
            # POST_ACCEL = 100
            compteur = 0

            while len(table) and compteur < acceleration: #wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
                compteur += 1
                if VERB:
                    print('+', end="")
                # trouver les lignes avec minimun de croix dans col
                large_col = [len(i) for i in table]
                min_col = min(large_col)
                ligne=[j for i in table for j in i if len(i) == min_col]                              
                ligne = list(set(ligne))
                # trouver à partir des croix pointées par ligne une colonne avec un maximum de croix
                col=[]
                for i in ligne:
                    cpt = 0
                    for j in table:
                            if i in j:
                                cpt += 1
                    col.append(cpt)
                
                num = ligne[col.index(max(col))]
                prereduction.append(num)
                table1 = []
                for i in table:
                    if not (num in i):
                        table1.append(i)
                table = table1
            if not len(table):
                if VERB and SYNTHESE:
                    print('\n Presynthesis: ', compteur, 'loop' )
                return [prereduction]
            
            # Petrick methode         
            s1= set(frozenset([i]) for i in table[0])      
            for t in table:
                if VERB:
                    print('*', end="")          
                s1=set((frozenset([i]) | j) for i in frozenset(t) for j in s1)               
                for i in s1:                   
                    s1={i if i < j else j for j in s1 }
            
            s1 = list(map(list,(s1)))
            s1=[i + prereduction  for i in s1]               
               
            return list(map(list,(s1)))
        
        """========================Simplification ============================"""
        SYNTHESE = False

        VERB = False
        if 'v' in self.arg_list and self.arg_list['v'] == True:
            VERB = True
        PRE_ACCEL = 0
        if 'a' in self.arg_list:
            PRE_ACCEL = self.arg_list['a']
        POS_ACCEL = 0
        if 'b' in self.arg_list:
            POST_ACCEL = self.arg_list['b']    
            
        POST = False
        if 'p' in self.arg_list and self.arg_list['p'] == True:
            POST = True 
        DETAIL = False
        if 'd' in self.arg_list and self.arg_list['d'] == True:
            DETAIL = True

        table_1, table_0, err = __expense_0_1(self.tbl_1, self.tbl_0)  # listes en binaires des termes 1 et 0

        if err:

            return [],[],[],True



        table_essentiel, table_1_restant = __terme_essentiel(table_1, table_0)
        if VERB:
            print( '\n-- discovered', len(table_essentiel), 'essential term(s) --')
            print('-- remains to be covered', len(table_1_restant), '--\n')

        table_terme_supl = __termes_supplementaires(table_1_restant, table_0)

        if VERB:
            print('\n\n -- discovered', len(table_terme_supl), 'additional term(s) --')

        tbl_synt, cpt= __tbl_synthese(table_1_restant, table_terme_supl)

        if VERB:
            print('\n-- Synthesis:', cpt, 'term(s) to cover', len(tbl_synt),'minterms remaining --\n')

        sol = []
        if POST and len(tbl_synt):
            SYNTHESE = True

            sol = __petrick(tbl_synt,POST_ACCEL)
            sol.sort(key=len)
            sol = [sorted(i) for i in sol]
            
            if VERB:
                print()
        return table_essentiel, table_terme_supl, sol,False

"""----------------------class end -----------------------------------------------------"""

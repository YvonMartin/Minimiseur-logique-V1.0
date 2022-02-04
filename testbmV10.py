# -*- coding: utf-8 -*-

"""
Minimal program (as an example) to simplify from a list contained in an 
input file *. txt in the folder /bench 
The file containing the result of the calculation is in the */bench=out directory and for name is *.out
for the direct form and *.outi for the reverse form

example : (essai1.txt)

.i 4
.o 1
0-0- 1
01-- 1
-11- 1
1000 1
1-01 0
001- 0
.e

gives as a result
gives different results according to the chosen option.
For example:
for a detailed simplification
with 'd' parameter (detailed solutions)

Direct form
Essential terms
  1  0-0-
  
Additional terms
  1  -1-0
  2  1-1-
  3  01--
  4  --00
  5  1--0
  6  -11-
  
Summary of the additional terms
  5 6  (2)
  4 6  (2)
  2 3 5  (3)
  2 3 4  (3)

option:
Output Numero:  output number
Reverse solution: i
Verbatim mode : v
For a detailed simplification : d
How many solutions to edit : number 1, 2...
        if 0, no synthesis  (one solution)
Pre-acceleration. Accelerates the search for terms
        number 0, 1, 2... if 0, no acceleration  (défault)
Post-acceleration . Accelerates synthesis (choice of terms)
        number 0, 1, 2... if 0, no acceleration  (défault)
if we want all solutions  pre and post acceleration numbers to 0       

"""

__author__ = 'Yvon Martin'
__version__ = "1.0"

from solveboolV10 import acqui_terme, decode_bin, Simply
import time
TYPE_FILE = '.txt'

def lecture_fichier(nom_fichier):
    error = False
    fichier_list = []
    try:
        with open('bench/'+ nom_fichier + TYPE_FILE, 'r') as fichier_in:
            lignes = fichier_in.readlines()
            for ligne in lignes:
                if ligne.rstrip() != '':
                    fichier_list.append(ligne.rstrip())
            fichier_list.reverse()
    except:
        error = True
    return fichier_list, error

def my_suite(*args):
    result = ''
    for x in args:
        result += str(x)+ ' '
    return result

def input_tables_01(data_in, num_out):
    """
    Decode the stack (alphabetical list of 3 characters '1-0') data_in to form
    the standardized list(s) of terms 1 and 0. Each element is a
    tuple (term, mask). the hidden bits of the term are normalized to 0
    """
    terme_0 = set()
    terme_1 = set()
    erreur = False
    nbr_variable = 0
    out_max = 1            

    while len(data_in) != 0:
        rep = data_in.pop()
        rep= rep.strip().split()
        if rep[0] == ".e":
            pass
        elif rep[0] == ".i":
            nbr_variable = int(rep[1])
        elif rep[0] == ".o":
            out_max = int(rep[1])
        elif nbr_variable == 0:
            terme_0 = set()
            terme_1 = set()
            erreur = True
            break
        else:
            terme, erreur = acqui_terme(rep[0], nbr_variable)
            if num_out > out_max:
                num_out = 1
                print("Incorrect output, default = 1")
            if erreur:
                terme_0 = set()
                terme_1 = set()
                break

            if rep[1][num_out - 1] == '1':
                terme_1.add(terme)
            elif rep[1][num_out - 1] == '0':
                terme_0.add(terme)

    return (nbr_variable, list(terme_1), list(terme_0),  erreur)  # liste normalisée

"""=============================================================================="""
def test():
    sortir = input('further simplification (y): ')
    if sortir != ('y' or 'Y'):
        FINISH = True
        exit()
"""===============================MAIN==========================================="""
FINISH = False
while not(FINISH):
    ERROR = 0
    while not(ERROR):
        print("Simplification of a logical function")
        print("=====================================")
        nom = input("file name: ")
        data_in, err = lecture_fichier(nom)  # contient le fichier des termes sous forme pile
        if err:
            ERROR = 1
           
        print("-----------------------------------------------------------")

        dat = data_in[:]
        if len(data_in) == 0:
            ERROR = 2
            break
        print("Terms to be simplified \n")
        while len(dat):
            print(dat.pop())
            
        print("------------------------------------------------------------")

        num = input("output Numero ")
        if num.isnumeric():
            num_out = abs(int(num))
        else:
            print("Incorrect output, default = 1")
            num_out = 1
        nbr_variable, t1, t0,  erreur = input_tables_01(data_in, num_out)  # listes normalisée: nbr de variable, terme1, terme0, erreur

        if erreur:
            ERROR = 3
            break

        extens = ".out1" 

        rep = input("If you want the reverse form, type i: ")
                
        ver = input("To verbatim type v: ")
        if ver == 'v':
            verb = True
        else:
            verb = False
            
        details= input("If you want all the additional terms, type d: ")
        if details == 'd':
            detail= True
        else:
            detail = False
        
        sol = input("how many solutions to edit (default: 1, none: 0): ")
        if not sol.isnumeric():
            nb_post = 1
        else:           
            nb_post = abs(int(sol))
        post = False
        pst = 'off'
        if nb_post != 0:
            post = True
            pst = 'on'
        
        pre_accel = input("If you want a pre-acceleration (search additional terms), type a number (0, 1..): ")
        if pre_accel.isnumeric():
            pre_acc = abs(int(pre_accel))
        else:
            print("Incorrect nombre, default = 0")
            pre_acc = 0
            
        post_accel = input("If you want a post-acceleration (Numero additional terms), type a number (0, 1..): ")
        if post_accel.isnumeric():
            post_acc = abs(int(post_accel))
        else:
            print("Incorrect nombre, default = 0")
            post_acc = 0           
        print("------------------------------------------------------------ ")

        start = time.time()

        posi = 0

        simply = Simply(nbr_variable, a = pre_acc, b = post_acc, v = verb, p = post, d = detail)

        if rep != "i":
            t_essentiel, t_supplementaire, nu_synthese,error = simply(t1,t0)
            if error:
                ERROR = 4
                break

            print("\n------------------------------------------\nDirect form\n")
        else:
            t_essentiel, t_supplementaire, nu_synthese,error = simply(t0,t1)

            if error:
                ERROR = 4
                break
            extens = ".out1i"     
            print("Inverse form")

        with open('bench-out/' + nom + extens, 'w') as fichier_out:
            print("Essential terms\n")

            fichier_out.write( nom + TYPE_FILE + '  -')
            if rep == 'i':
                fichier_out.write('Inverse form-\n\n')
            else:
                fichier_out.write('Direct forme-\n\n')
            si= "no"
            if detail:
                si="yes"   
                
            fichier_out.write( 'All additionnel terms: ' + si +'\n')
            fichier_out.write( 'Output numero: ' + str(num_out) + '\n')
            fichier_out.write( 'Post synthese: ' + pst + '\n')
            if nb_post != 0:
                fichier_out.write( 'Number of solutions limited to: ' + str(nb_post) + '\n')
            
            fichier_out.write( 'Pre_accelerate: ' + str(pre_acc) +'\n')
            fichier_out.write( 'Post_accelerate: ' + str(post_acc) +'\n\n')
            
            fichier_out.write("Essential terms\n\n")

            tt_ess = [decode_bin(i, nbr_variable )for i in t_essentiel]

            for index, i in enumerate(tt_ess):
                ff = f"{index + 1:>3d} {i} "
                print(ff)
                fichier_out.write(i + "\n")

            print("\nAdditional terms\n")

            tt_sup = [decode_bin(i, nbr_variable )for i in t_supplementaire]


            fichier_out.write("\nAdditional terms\n\n")
            tt_sup = [decode_bin(i, nbr_variable )for i in t_supplementaire]

            for index, i in enumerate(tt_sup):
                ff = f"{index + 1:>3d} {i}"
                print(ff)
                fichier_out.write(ff + "\n")

            print("\n------------------------------------------\nSummary of the additional terms\n")
            fichier_out.write("\nSummary of the additional terms\n\n")
           
            for i in nu_synthese[0:nb_post]:

                    print(" ", my_suite(*i)," (" + str(len(i)) + ")")
                    fichier_out.write("  " + my_suite(*i) + " (" + str(len(i)) + ")\n")
            end = time.time()
            
            
            
            
            print("\n------------------------------------------")
            tp ='time to execute ' +str(int((end-start)*1000)) +' ms'
            print(tp)

            fichier_out.write("\n" + tp + "\n")
            fichier_out.close()

        if ERROR == 0:
            test()

    if ERROR == 1:
        print("---- Error: file name \n")
        test()
    elif ERROR == 2:
        print("---- Error: empty file \n")
        test()
    elif ERROR == 3:
        print("---- Error in list of entries ----\n")
        test()
    elif ERROR == 4:
        print("---- Error: terms 0 cover terms 1 ----\n\n")

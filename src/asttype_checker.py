from ast import *
from asttypes import *

#Start med at modtage det tree som vi har lavet i AST generator

#Vi skal også imens vi gennemløber, tjekke om typerne i procedure kald er OK, og om variablerne er defineret / erklæret. Aka, liste over alle de forskellige variabler, lister, attributes (Gælder kun registers)
#Det samme gælder funktioner, men vi skal nok løbe dem igennem først, da funktionskald gerne skulle kunne placeres hvor end.

#Den skal nok køre et loop igennem de forskellige statements? Det giver ikke mening at lade tjekke om program er OK ud fra de forskellige statements, ikke engang alle statements behøver at blie tjekket
#Brug visitor pattern eller generic recursive function til at besøge alle noderne, 
# og fra bunden så finde den nuværende nodes typer, underliggende, på den vis at lade typen florere op

#I løbet af denne process, bliver semantikken tjekket om den er OK, 
#ift. godtagning af de forskellige nodes der tjekkes, efter alle childrens typer er gået op i træet

#Efter denne gennemløbning, kan vi returnere det samme træ som vi arbejdede på, da vi kun ændrer typerne på det.
#Kører det igennem uden fejl, er der ingen semantiske fejl, og det er nu et TAAST



#OKAY MERE KONKRET

#Gennemløb erklæringer / definitioner af variabler og funktioner, og tilføj dem til en liste der OGSÅ indeholder hardware registers
#Typetjek dem imens?


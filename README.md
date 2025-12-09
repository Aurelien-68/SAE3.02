# SAE3.02
Nom du groupe: πThon  
Membres du groupe:  
    - HENRY Aurelien  
    - HALTER Mathis

Description du projet:  
&nbsp;&nbsp;&nbsp;&nbsp;Ce projet implemente un systeme de routage en oignon. Le systeme se compose d'un Master qui vas recuperer et envoyer les clés publiques, il y a egalement des routeurs virtuels et des clients qui pouront envoyer des messages en plusieurs couches de chiffrement pour garantir l'anonymat.

Fonctionalités:  
&nbsp;&nbsp;&nbsp;&nbsp;- Routage multi-sauts avec sockets Python  
&nbsp;&nbsp;&nbsp;&nbsp;- Gestion multithread des connexions  
&nbsp;&nbsp;&nbsp;&nbsp;- Chiffrement asymétrique (clé publique/privée simplifiée)  
&nbsp;&nbsp;&nbsp;&nbsp;- Anonymisation par couches (routage en oignon)  
&nbsp;&nbsp;&nbsp;&nbsp;- Base de données MariaDB (clés, tables de routage)  
&nbsp;&nbsp;&nbsp;&nbsp;- Interface Qt (visualisation des connexions, statistiques,client)  


Commandes pour lancement des different programme:

python master.py -p MON_PORT

python router.py -m IP_MASTER:PORT_MASTER -p MON_PORT

python client.py -m IP_MASTER:PORT_MASTER -p MON_PORT

ARBORESCENCE DU PROJET:  
SAE3.02  
&nbsp;&nbsp;&nbsp;&nbsp;|   
&nbsp;&nbsp;&nbsp;&nbsp;|_Prototypes  
&nbsp;&nbsp;&nbsp;&nbsp;|_Source  
&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;|_master.py  
&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;|_router.py  
&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;|_client.py  
&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;|_primes.py  
&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;|_rsa_utils.py  
&nbsp;&nbsp;&nbsp;&nbsp;|  
&nbsp;&nbsp;&nbsp;&nbsp;|_Documentations

DOCUMENTATIONS:  
Documentation utilisateur:  
Documentation d'instalation:  
Document de réponse: 

LIEN DE LA VIDEO:  

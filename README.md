# SAE3.02
Nom du groupe: πThon  
Membres du groupe:  
   &nbsp;&nbsp;&nbsp;&nbsp; - HENRY Aurelien  
   &nbsp;&nbsp;&nbsp;&nbsp; - HALTER Mathis

Description du projet:  
&nbsp;&nbsp;&nbsp;&nbsp;Ce projet implémente un système de routage en oignon. Le système se compose d'un Master qui vas récupérer et envoyer les clés publiques, il y a également des routeurs virtuels et des clients qui pourront envoyer des messages en plusieurs couches de chiffrement pour garantir l'anonymat.

Fonctionnalités:  

&nbsp;&nbsp;&nbsp;&nbsp;- Routage multi-sauts avec sockets Python  
&nbsp;&nbsp;&nbsp;&nbsp;- Gestion multithread des connexions  
&nbsp;&nbsp;&nbsp;&nbsp;- Chiffrement asymétrique (clé publique/privée simplifiée)  
&nbsp;&nbsp;&nbsp;&nbsp;- Anonymisation par couches (routage en oignon)  
&nbsp;&nbsp;&nbsp;&nbsp;- Base de données MariaDB (clés, tables de routage)  
&nbsp;&nbsp;&nbsp;&nbsp;- Interface Qt (visualisation des connexions, statistiques, client)  

Librairies utilisées:  
&nbsp;&nbsp;&nbsp;&nbsp;- random  
&nbsp;&nbsp;&nbsp;&nbsp;- math  
&nbsp;&nbsp;&nbsp;&nbsp;- socket  
&nbsp;&nbsp;&nbsp;&nbsp;- threading  
&nbsp;&nbsp;&nbsp;&nbsp;- time  
&nbsp;&nbsp;&nbsp;&nbsp;- sys  
&nbsp;&nbsp;&nbsp;&nbsp;- PyQt5  
&nbsp;&nbsp;&nbsp;&nbsp;- mysql.connector  


Commandes pour lancement des différents programmes:

&nbsp;&nbsp;&nbsp;&nbsp; python master.py -p MON_PORT --db-user NOM_USER --db-pass MDP_DE_LA_DB

&nbsp;&nbsp;&nbsp;&nbsp;python router.py -n IP_DU_MASTER:PORT_DU_MASTER -p MON_PORT

&nbsp;&nbsp;&nbsp;&nbsp;python client.py -n IP_DU_MASTER:PORT_DU_MASTER -p MON_PORT

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
&nbsp;&nbsp;&nbsp;&nbsp;Documentation d'installation:  \Documentations\Document_installation  
&nbsp;&nbsp;&nbsp;&nbsp;Documentation utilisateur:  \Documentations\Document_utilisation  
&nbsp;&nbsp;&nbsp;&nbsp;Document de réponse: \Documentations\Document_réponse  

LIEN DE LA VIDEO DE DEMONSTRATION DU PROJET:  https://youtu.be/NMS4P1LkhDw


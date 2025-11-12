import threading
import time

def compte_a_rebours(n, nom_thread):
    while n > 0:
        print(f"{nom_thread} : {n}")
        n -= 1
        time.sleep(0.5)  # petite pause pour voir l’alternance entre les threads

# Création des threads avec des valeurs de départ différentes
thread1 = threading.Thread(target=compte_a_rebours, args=(5, "thread 1"))
thread2 = threading.Thread(target=compte_a_rebours, args=(3, "thread 2"))

# Démarrage des threads
thread1.start()
thread2.start()

# Attente de la fin des deux threads
thread1.join()
thread2.join()

print("Fin du programme")

import threading
import time

# Fonction exécutée par le premier thread
def thread1():
    for i in range(5):
        print("Je suis la thread 1")
        time.sleep(0.5)  # petit délai pour alterner les affichages

# Fonction exécutée par le second thread
def thread2():
    for i in range(5):
        print("Je suis la thread 2")
        time.sleep(0.5)

# Création des threads
t1 = threading.Thread(target=thread1)
t2 = threading.Thread(target=thread2)

# Lancement des threads
t1.start()
t2.start()

# Attente de la fin des deux threads
t1.join()
t2.join()

print("Les deux threads sont terminés.")

def lire_fichier(nom_fichier):
    f = None
    try:
        print(f"Ouverture du fichier : {nom_fichier}")
        f = open(nom_fichier, "r")

        for ligne in f:
            ligne = ligne.rstrip("\n\r")
            print(ligne)

    except FileNotFoundError:
        print("Erreur : le fichier n'existe pas.")

    except FileExistsError:
        print("Erreur : un fichier portant ce nom existe déjà (cas rare en lecture).")

    except PermissionError:
        print("Erreur : vous n'avez pas les droits pour lire ce fichier.")

    except IOError:
        print("Erreur d'entrée/sortie lors de la manipulation du fichier.")

    else:
        print("\nLecture terminée sans erreur.")

    finally:
        if f is not None:
            f.close()
        print("Fin du programme.")



nom = input("Nom du fichier à lire : ")
lire_fichier(nom)

def lire_fichier_with(nom_fichier):
    try:
        print(f"Ouverture du fichier : {nom_fichier}")

        with open(nom_fichier, "r") as f:
            for ligne in f:
                ligne = ligne.rstrip("\n\r")
                print(ligne)

    except FileNotFoundError:
        print("Erreur : le fichier demandé n'existe pas.")

    except FileExistsError:
        print("Erreur : conflit de fichier.")

    except PermissionError:
        print("Erreur : permission refusée, vous ne pouvez pas lire ce fichier.")

    except IOError:
        print("Erreur d'entrée/sortie avec le fichier.")

    else:
        print("\nLecture terminée sans erreur.")

    finally:
        print("Fin du programme.")


nom = input("Nom du fichier à lire : ")
lire_fichier_with(nom)

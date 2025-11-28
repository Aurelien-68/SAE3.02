def divEntier(x: int, y: int) -> int:
    if y == 0:
        raise ZeroDivisionError("Division par zéro impossible.")

    if x < 0 or y < 0:
        raise ValueError("Les deux valeurs doivent être positives.")

    if x < y:
        return 0
    else:
        x = x - y
        return divEntier(x, y) + 1


def main():
    try:
        x = int(input("Valeur de x : "))
        y = int(input("Valeur de y : "))

        resultat = divEntier(x, y)

    except ValueError as err:
        print(f"Erreur : {err}")

    except ZeroDivisionError as err:
        print(f"Erreur : {err}")

    else:
        print(f"Résultat de la division entière : {resultat}")

    finally:
        print("Fin du programme.")


if __name__=="__main__":
    main()

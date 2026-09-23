"""FICHIER JETABLE - NE PAS MERGER.

Sert uniquement a verifier que Snyk s'execute sur les pull requests de ce repo.
Contient volontairement un motif non securise (injection de commande) que Snyk
Code doit signaler. A supprimer avec la branche test/snyk-trigger-check.
"""

import os


def run_report(user_input):
    # Injection de commande volontaire : le parametre est concatene dans le shell.
    os.system("echo " + user_input)

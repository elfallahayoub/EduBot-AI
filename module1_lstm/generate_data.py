import random
import json
import os

data = {

    "SALUTATION": {
        "debuts": [
            "bonjour", "salut", "bonsoir", "hello", "coucou",
            "hey", "hi", "bonsoir", "bien le bonjour",
            "bonjour à vous", "salut à vous",
            "bonjour je voudrais", "bonjour j'aurais",
            "bonsoir j'ai", "salut j'aurais besoin",
            "bonjour est ce que vous pouvez",
            "bonjour pouvez vous m'aider",
            "bonjour j'ai besoin", "salut j'ai besoin",
            "bonjour je cherche", "salut je cherche",
            "bonjour je veux", "salut je veux",
            "bonjour j'aimerais", "salut j'aimerais",
            "bonjour j'aurais une question",
            "bonsoir j'aurais une question",
            "bonjour puis-je vous demander",
            "salut puis-je vous poser une question",
            "bonjour permettez-moi de vous demander",
            "bonjour excusez-moi",
            "bonjour pardon",
            "bonjour s'il vous plaît",
            "bonjour je me permets de vous contacter",
            "salut je me permets de vous écrire"
        ],
        "suites": [
            "j'ai besoin d'aide", "j'ai une question",
            "je cherche une information", "je cherche des informations",
            "vous êtes disponible", "vous êtes là",
            "je veux poser une question", "je voudrais poser une question",
            "j'ai besoin d'une information", "j'ai besoin de renseignements",
            "je veux de l'aide", "je voudrais de l'aide",
            "j'ai besoin d'un renseignement", "je cherche de l'aide",
            "j'ai un problème", "aidez moi s'il vous plaît",
            "j'ai besoin d'un conseil", "j'aurais une question",
            "pouvez vous m'aider", "pouvez vous me renseigner",
            "je veux savoir quelque chose", "j'ai une demande",
            "je veux des informations", "je cherche à me renseigner",
            "comment ça marche ici", "je suis étudiant j'ai besoin d'aide",
            "je cherche des renseignements sur l'université",
            "j'ai besoin de vous parler", "j'ai quelque chose à demander",
            "je voudrais me renseigner", "je veux me renseigner",
            "j'ai une petite question", "j'ai une question rapide",
            "j'ai une question importante", "j'ai une question urgente",
            "j'aurais besoin d'informations", "j'aurais besoin d'aide",
            "je voudrais des informations", "je souhaite me renseigner",
            "je souhaite obtenir des informations",
            "je souhaite avoir des renseignements",
            "je désire obtenir des informations",
            "permettez-moi de vous poser une question",
            "j'espère que vous pourrez m'aider",
            "j'espère que vous pouvez m'aider",
            "je fais appel à vous pour",
            "je me permets de vous demander",
            "est ce que vous pouvez me renseigner",
            "est ce que je peux vous poser une question",
            "est ce que vous pouvez m'aider",
            "est ce possible d'avoir de l'aide",
            "", "comment allez vous", "ça va",
            "j'espère que vous allez bien"
        ],
        "fins": [
            "", " merci", " s'il vous plaît", " svp",
            " stp", " !", " ?", " merci d'avance",
            " je vous en remercie d'avance",
            " en vous remerciant d'avance"
        ]
    },

    "DEMANDE_CONSEIL": {
        "situations": [
            "j'ai raté", "j'ai échoué à", "j'ai échoué en",
            "j'ai eu de mauvaises notes en", "j'ai eu un mauvais résultat en",
            "je n'ai pas réussi", "je n'ai pas eu la moyenne en",
            "j'ai eu moins de dix en", "j'ai eu zéro en",
            "je suis en difficulté en", "je suis en difficulté pour",
            "je suis perdu en", "je suis perdu dans",
            "j'ai du mal en", "j'ai du mal avec",
            "je comprends rien en", "je ne comprends rien en",
            "je n'arrive pas à comprendre", "j'arrive pas à comprendre",
            "je suis nul en", "je suis mauvais en",
            "mes notes sont catastrophiques en",
            "mes résultats sont très mauvais en",
            "mes résultats sont insuffisants en",
            "je suis en train de rater", "je vais rater",
            "j'ai peur de rater", "je stresse pour",
            "j'angoisse pour", "je suis stressé par",
            "je suis inquiet pour", "j'ai du mal avec",
            "j'ai un problème avec", "je galère avec",
            "je bloque sur", "je n'arrive pas à suivre",
            "j'arrive pas à suivre", "je ne suis pas capable de",
            "je suis incapable de comprendre",
            "j'ai beaucoup de difficultés en",
            "j'éprouve des difficultés en",
            "je rencontre des difficultés en",
            "j'ai des lacunes en", "je manque de bases en",
            "mon niveau est très faible en",
            "mon niveau est insuffisant en",
            "je ne suis pas au niveau en"
        ],
        "matieres": [
            "mon examen", "mes examens", "mes cours",
            "les maths", "la physique", "l'informatique",
            "l'anglais", "le français", "la chimie",
            "la biologie", "l'arabe", "les sciences",
            "ma licence", "mon master", "mes études",
            "le module un", "le module deux", "le module trois",
            "cette matière", "ce cours", "ce module",
            "mon semestre", "mes résultats", "ma moyenne",
            "l'algorithmique", "la programmation",
            "les bases de données", "les réseaux",
            "les mathématiques", "l'analyse",
            "l'algèbre", "la statistique",
            "la mécanique", "l'électronique",
            "la comptabilité", "l'économie",
            "le droit", "la gestion",
            "toutes les matières", "toutes mes matières",
            "l'ensemble des matières", "plusieurs matières"
        ],
        "demandes": [
            "aide moi", "qu'est-ce que je peux faire",
            "que faire", "donne moi des conseils",
            "conseille moi", "oriente moi",
            "dis moi quoi faire", "j'ai besoin d'aide",
            "comment je peux m'en sortir",
            "comment je peux progresser",
            "comment améliorer ça", "comment réussir",
            "comment travailler", "aide moi s'il vous plaît",
            "j'ai besoin de tes conseils",
            "qu'est-ce que tu me conseilles",
            "comment je dois faire", "par où commencer",
            "donne moi un plan", "aide moi à m'organiser",
            "comment réviser efficacement",
            "comment organiser mes révisions",
            "comment organiser mon temps",
            "comment planifier mes révisions",
            "comment planifier mon travail",
            "comment améliorer mes résultats",
            "comment améliorer mes notes",
            "comment améliorer ma moyenne",
            "comment rattraper mon retard",
            "comment combler mes lacunes",
            "comment progresser rapidement",
            "comment travailler efficacement",
            "comment étudier correctement",
            "comment bien préparer les examens",
            "comment réussir mes examens",
            "comment passer mes examens",
            "donne moi une méthode de travail",
            "donne moi une stratégie de révision",
            "j'ai besoin d'une méthode",
            "j'ai besoin d'un plan de travail",
            "j'ai besoin d'un plan de révision",
            "je veux réussir dis moi comment",
            "je veux progresser dis moi comment",
            "je veux m'améliorer dis moi comment",
            "aidez moi à réussir",
            "aidez moi à progresser",
            "aidez moi à m'améliorer"
        ],
        "fins": [
            "", " ?", " svp", " stp", " merci",
            " j'en ai vraiment besoin", " c'est urgent",
            " s'il vous plaît", " please",
            " je vous en supplie", " aidez moi",
            " j'ai besoin de votre aide"
        ]
    },

    "DEMANDE_TITRE_COURS": {
        "debuts": [
            "c'est quoi le titre", "quel est le titre",
            "donne moi le titre", "je veux le titre",
            "dis moi le titre", "c'est quoi le nom",
            "quel est le nom", "donne moi le nom",
            "je veux le nom", "dis moi le nom",
            "c'est quoi l'intitulé", "quel est l'intitulé",
            "donne moi l'intitulé", "je veux l'intitulé",
            "je cherche le titre", "je cherche le nom",
            "je cherche l'intitulé", "je cherche l'appellation",
            "tu connais le titre", "tu sais le titre",
            "vous connaissez le titre", "vous savez le titre",
            "j'ai besoin du titre", "j'ai besoin du nom",
            "j'ai besoin de l'intitulé",
            "quelle est la matière", "comment s'appelle",
            "comment il s'appelle", "comment se nomme",
            "comment est intitulé", "quel est le contenu",
            "c'est quoi exactement", "expliquez moi c'est quoi",
            "renseignez moi sur", "donnez moi des infos sur",
            "j'aimerais connaître le titre",
            "j'aimerais connaître le nom",
            "j'aimerais connaître l'intitulé",
            "pouvez vous me donner le titre",
            "pouvez vous me donner le nom",
            "pourriez vous me donner le titre",
            "pourriez vous me donner le nom",
            "je voudrais connaître le titre",
            "je voudrais connaître le nom",
            "je souhaite connaître le titre",
            "est ce que vous pouvez me donner le titre",
            "est ce que vous connaissez le titre",
            "quelle est l'appellation exacte",
            "quel est le titre exact",
            "quel est le nom exact",
            "quel est l'intitulé exact",
            "donnez moi le titre exact",
            "donnez moi le nom exact"
        ],
        "elements": [
            "du cours", "du module", "du chapitre",
            "de la matière", "de l'unité d'enseignement",
            "de l'ue", "de la séance", "du td",
            "du tp", "du cm", "de la leçon",
            "de l'enseignement", "de l'unité",
            "de la formation", "du programme"
        ],
        "numeros": [
            "un", "deux", "trois", "quatre", "cinq",
            "six", "sept", "huit", "neuf", "dix",
            "1", "2", "3", "4", "5",
            "6", "7", "8", "9", "10",
            "numéro un", "numéro deux", "numéro trois",
            "numéro quatre", "numéro cinq", "numéro six",
            "numéro sept", "numéro huit", "numéro neuf",
            "numéro dix", "numéro 1", "numéro 2",
            "numéro 3", "numéro 4", "numéro 5",
            "premier", "deuxième", "troisième",
            "quatrième", "cinquième", "sixième",
            "septième", "huitième", "neuvième",
            "du premier semestre", "du deuxième semestre",
            "de cette semaine", "de la semaine prochaine",
            "d'aujourd'hui", "de demain", "de lundi",
            "de mardi", "de mercredi", "de jeudi", "de vendredi"
        ],
        "fins": [
            "", " ?", " svp", " stp", " s'il vous plaît",
            " merci", " j'en ai besoin", " c'est urgent",
            " s'il te plaît", " please", " rapidement",
            " merci d'avance", " je vous remercie"
        ]
    },

    "INFO_INSCRIPTION": {
        "debuts": [
            "c'est quoi la date limite",
            "quelle est la date limite",
            "c'est quand la date limite",
            "quand ferment les inscriptions",
            "quand ferme l'inscription",
            "quand clôturent les inscriptions",
            "comment s'inscrire",
            "comment faire pour s'inscrire",
            "comment je peux m'inscrire",
            "je veux m'inscrire",
            "je voudrais m'inscrire",
            "je veux faire mon inscription",
            "je voudrais faire mon inscription",
            "comment faire mon inscription",
            "comment faire une inscription",
            "je veux créer mon dossier",
            "je voudrais créer mon dossier",
            "comment créer mon dossier",
            "comment constituer mon dossier",
            "comment préparer mon dossier",
            "comment monter mon dossier",
            "quels documents pour s'inscrire",
            "quels documents fournir pour s'inscrire",
            "quels documents dois je fournir",
            "quelles pièces fournir",
            "quelles pièces joindre",
            "quels justificatifs fournir",
            "c'est où l'inscription",
            "où est-ce qu'on s'inscrit",
            "où faire l'inscription",
            "où déposer le dossier",
            "c'est quoi la procédure",
            "quelle est la procédure",
            "quelles sont les démarches",
            "comment ça marche l'inscription",
            "les inscriptions sont ouvertes",
            "est ce que les inscriptions sont ouvertes",
            "est ce que les inscriptions sont encore ouvertes",
            "quand ouvrent les inscriptions",
            "quand commencent les inscriptions",
            "quand débutent les inscriptions",
            "j'ai besoin d'aide pour l'inscription",
            "je veux des infos sur l'inscription",
            "je veux me renseigner sur l'inscription",
            "comment valider mon inscription",
            "comment finaliser mon inscription",
            "comment confirmer mon inscription",
            "les étapes pour s'inscrire",
            "la procédure d'inscription",
            "les démarches d'inscription",
            "les formalités d'inscription",
            "les conditions d'inscription",
            "comment rejoindre l'université",
            "comment intégrer l'université",
            "comment s'inscrire à l'université",
            "comment s'inscrire à la fac",
            "comment s'inscrire en licence",
            "comment s'inscrire en master",
            "comment s'inscrire en première année",
            "comment s'inscrire en deuxième année"
        ],
        "elements": [
            "d'inscription", "des inscriptions",
            "pour s'inscrire", "pour l'inscription",
            "à l'université", "à la fac",
            "au master", "en licence",
            "en première année", "en deuxième année",
            "en troisième année", "au département informatique",
            "à la formation", "au cursus",
            "au programme", "à la filière"
        ],
        "fins": [
            "", " ?", " svp", " stp", " s'il vous plaît",
            " merci", " c'est urgent", " j'ai besoin de savoir",
            " dites moi", " expliquez moi", " merci d'avance",
            " je vous remercie", " rapidement s'il vous plaît"
        ]
    },

    "INFO_EXAMEN": {
        "debuts": [
            "c'est quand", "quand est", "à quelle date",
            "quel jour", "quelle est la date de",
            "dis moi quand", "je veux savoir quand",
            "tu sais quand", "quand commence",
            "quand débute", "quand a lieu", "quand se passe",
            "quand est prévu", "quelle date pour",
            "je cherche la date de", "info sur la date de",
            "renseigne moi sur la date de",
            "je veux la date de", "donne moi la date de",
            "c'est à quelle heure", "à quelle heure commence",
            "à quelle heure débute", "à quelle heure a lieu",
            "quelle est l'heure de", "où se passe",
            "c'est dans quelle salle", "quelle salle pour",
            "dans quelle salle se déroule",
            "dans quelle salle a lieu",
            "c'est quoi le programme de",
            "quel est le programme de",
            "qu'est-ce qui sort à", "c'est quoi qui va sortir à",
            "le planning de", "le calendrier de",
            "les dates de", "quand passent",
            "est ce que l'examen est reporté",
            "est ce que le contrôle est reporté",
            "est ce que l'épreuve est reportée",
            "l'examen est maintenu",
            "le contrôle est maintenu",
            "dans combien de jours",
            "dans combien de temps",
            "les épreuves commencent quand",
            "le calendrier des épreuves",
            "le programme des épreuves",
            "les convocations pour",
            "la convocation pour"
        ],
        "sujets": [
            "l'examen", "le contrôle", "le ds",
            "le partiel", "l'épreuve", "le test",
            "l'exam", "les examens", "le contrôle final",
            "l'examen final", "le rattrapage",
            "l'exam de rattrapage", "l'évaluation",
            "le contrôle continu", "le cc",
            "l'examen semestriel", "le bilan",
            "les épreuves", "les contrôles",
            "les partiels", "les évaluations",
            "l'examen blanc", "le contrôle blanc",
            "la session", "la session d'examen",
            "la session de rattrapage"
        ],
        "matieres": [
            "de maths", "de mathématiques", "de physique",
            "d'informatique", "d'anglais", "de français",
            "de chimie", "de biologie", "d'arabe",
            "du module un", "du module deux", "du module trois",
            "du module quatre", "du module cinq", "du module six",
            "du semestre un", "du semestre deux",
            "du premier semestre", "du deuxième semestre",
            "de fin d'année", "de fin de semestre",
            "de la session un", "de la session deux",
            "de rattrapage", "final", "principal",
            "de l'algorithmique", "de la programmation",
            "des bases de données", "des réseaux",
            "de l'analyse", "de l'algèbre",
            "de la statistique", "de la mécanique",
            "de la comptabilité", "de l'économie",
            "de la prochaine session", ""
        ],
        "fins": [
            "", " ?", " svp", " stp", " s'il vous plaît",
            " merci", " j'en ai besoin", " c'est urgent",
            " dites moi", " j'aimerais savoir",
            " merci d'avance", " je vous remercie",
            " rapidement s'il vous plaît"
        ]
    },

    "AU_REVOIR": {
        "debuts": [
            "au revoir", "bye", "bye bye", "à bientôt",
            "à plus", "à plus tard", "à tout à l'heure",
            "à demain", "à la prochaine", "ciao",
            "tchao", "bonne journée", "bonne soirée",
            "bonne continuation", "bonne chance",
            "à très bientôt", "on se revoit bientôt",
            "à la prochaine fois", "jusqu'à la prochaine fois",
            "bonne fin de journée", "bonne fin de soirée",
            "passez une bonne journée", "passez une bonne soirée",
            "je vous souhaite une bonne journée",
            "je vous souhaite une bonne soirée"
        ],
        "merci": [
            "merci", "merci beaucoup", "merci infiniment",
            "merci mille fois", "grand merci",
            "je vous remercie", "je te remercie",
            "merci bien", "c'est gentil merci",
            "merci pour l'aide", "merci pour tout",
            "merci pour les informations",
            "merci pour les renseignements",
            "merci pour votre aide",
            "merci pour votre aide précieuse",
            "merci pour votre temps",
            "merci pour votre disponibilité",
            "je vous remercie pour votre aide",
            "je vous remercie pour votre aide précieuse",
            "je vous remercie pour votre temps",
            "je vous remercie pour votre disponibilité",
            "j'apprécie beaucoup votre aide",
            "c'est très aimable de votre part",
            "vous avez été très utile",
            "tu as été très utile",
            "vous m'avez beaucoup aidé",
            "vous m'avez été d'une grande aide",
            "votre aide m'a été très précieuse",
            "merci énormément",
            "un grand merci",
            "merci du fond du cœur"
        ],
        "confirmations": [
            "c'est tout", "j'ai eu ma réponse",
            "c'est ce que je cherchais",
            "ça m'aide beaucoup", "c'est suffisant",
            "c'est bon pour moi", "j'ai tout ce qu'il me faut",
            "c'est parfait", "excellent", "super", "parfait",
            "ok c'est noté", "c'est clair maintenant",
            "j'ai compris", "je comprends maintenant",
            "ça marche", "nickel", "très bien",
            "c'est exactement ce qu'il me fallait",
            "c'est exactement ce que je cherchais",
            "vous avez répondu à ma question",
            "ma question a trouvé sa réponse",
            "je n'ai plus de questions",
            "je reviendrai si j'ai d'autres questions",
            "je reviendrai si besoin",
            "voilà c'est tout ce que je voulais",
            "voilà c'est tout ce que je voulais savoir",
            "c'est tout ce dont j'avais besoin",
            "j'ai toutes les informations qu'il me faut",
            "je suis satisfait de la réponse",
            "la réponse est complète merci", ""
        ],
        "fins": [
            "", " !", " merci encore",
            " encore merci", " bonne journée",
            " bonne soirée", " à bientôt"
        ]
    }
}


def generer_phrases(intention, cible=50000):
    phrases    = set()
    comps      = data[intention]
    tentatives = 0
    max_t      = cible * 15

    while len(phrases) < cible and tentatives < max_t:
        tentatives += 1

        if intention == "SALUTATION":
            d = random.choice(comps["debuts"])
            s = random.choice(comps["suites"])
            f = random.choice(comps["fins"])
            p = f"{d} {s}{f}".strip() if s else f"{d}{f}".strip()

        elif intention == "DEMANDE_TITRE_COURS":
            d = random.choice(comps["debuts"])
            e = random.choice(comps["elements"])
            n = random.choice(comps["numeros"])
            f = random.choice(comps["fins"])
            p = f"{d} {e} {n}{f}".strip()

        elif intention == "DEMANDE_CONSEIL":
            s = random.choice(comps["situations"])
            m = random.choice(comps["matieres"])
            d = random.choice(comps["demandes"])
            f = random.choice(comps["fins"])
            p = f"{s} {m} {d}{f}".strip()

        elif intention == "INFO_INSCRIPTION":
            d = random.choice(comps["debuts"])
            e = random.choice(comps["elements"])
            f = random.choice(comps["fins"])
            if random.random() > 0.5:
                p = f"{d} {e}{f}".strip()
            else:
                p = f"{d}{f}".strip()

        elif intention == "INFO_EXAMEN":
            d = random.choice(comps["debuts"])
            s = random.choice(comps["sujets"])
            m = random.choice(comps["matieres"])
            f = random.choice(comps["fins"])
            p = f"{d} {s} {m}{f}".strip()

        elif intention == "AU_REVOIR":
            m  = random.choice(comps["merci"])
            c  = random.choice(comps["confirmations"])
            db = random.choice(comps["debuts"])
            f  = random.choice(comps["fins"])

            choix = random.randint(0, 4)
            if choix == 0:
                p = f"{m} {db}{f}"
            elif choix == 1:
                p = f"{db} {m}{f}"
            elif choix == 2:
                p = f"{m} {c}{f}"
            elif choix == 3:
                p = f"{c} {db}{f}"
            else:
                p = f"{m}{f}"

        p = p.strip()
        if len(p) > 3:
            phrases.add(p.lower())

    return list(phrases)


def generer_dataset(cible=50000):
    dataset = {}
    total   = 0

    for intention in data.keys():
        print(f"Generation : {intention}...")
        phrases = generer_phrases(intention, cible=cible)
        dataset[intention] = phrases
        total += len(phrases)
        print(f"  {intention} : {len(phrases):,} phrases")

    print(f"\nTotal : {total:,} phrases")

    with open("dataset_complet.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    taille = os.path.getsize("dataset_complet.json") / 1024 / 1024
    print(f"Sauvegarde : dataset_complet.json ({taille:.1f} MB)")

    return dataset


if __name__ == "__main__":
    generer_dataset(cible=50000)

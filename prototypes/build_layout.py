"""Generate a standalone, synthetic layout spike; not the production renderer."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
HEADER = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[margin=20mm,headheight=15pt]{geometry}
\usepackage{longtable,array,fancyhdr}
\usepackage[hidelinks]{hyperref}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{Famille Exemple -- prototype fictif}
\fancyhead[R]{\thepage}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}
\newcommand{\sourcecall}{\footnote{Registre fictif, citation [1]. Annexe : page~\pageref{citation:1}.}}
\begin{document}
\thispagestyle{empty}
\vspace*{30mm}
{\Huge Livre de la famille Exemple}\par
{\Large Prototype de composition L2}\par
\vspace{15mm}
\fbox{\parbox[c][35mm][c]{.4\linewidth}{\centering Portrait fictif A}}
\hfill
\fbox{\parbox[c][35mm][c]{.4\linewidth}{\centering Portrait fictif B}}
\vfill
Données entièrement inventées. Les cadres représentent des ressources à intégrer.
Ce document explore les renvois, les notes et les continuations ; il ne valide pas le moteur généalogique.
\newpage
\section*{Mode de lecture}
L'ascendance commence par le couple central. Les événements familiaux sont détaillés une seule fois.
Les citations peuvent justifier plusieurs faits et gardent une entrée unique en annexe.
Les grandes parties commencent sur une page nouvelle ; les fiches longues continuent librement.
\tableofcontents
\newpage
\section{Couple central -- génération 0}\label{family:0}
\subsection*{Émile Exemple et Jeanne Fictive}
\begin{tabular}{p{.45\linewidth}p{.45\linewidth}}
Émile Exemple & Jeanne Fictive \\
Naissance : 1880, lieu fictif & Naissance : vers 1882, lieu fictif
\end{tabular}
\subsection*{Événement familial}
Union, 1905, commune fictive.\sourcecall
Les fiches individuelles renvoient à cette section : aucun événement familial n'y est développé une seconde fois.
\subsection*{Enfants}
Camille Exemple (1906), voir page~\pageref{person:child}.
\newpage
\section{Ascendance -- génération -1}\label{ancestor:1}
\subsection*{Famille ancienne peu documentée}
Deux parents connus, dates partielles. Les champs absents ne sont pas inventés.
Une personne ne présentant que naissance et décès reste une mention, sans fiche automatique.
\newpage
\section{Émile Exemple -- fiche longue}\label{person:emile}
Naissance : 1880. Activités et résidences ci-dessous sont fictives.\sourcecall
\begin{longtable}{p{.15\linewidth}p{.77\linewidth}}
\textbf{Date}&\textbf{Événement}\\\hline\endfirsthead
\textbf{Date}&\textbf{Événement -- suite}\\\hline\endhead
"""


def build():
    rows = []
    for i in range(85):
        rows.append(
            f"{1900 + i // 4} & Résidence fictive {i + 1}. Description conservée avec accents : "
            r"Émile, métier d'artisan, lieu imaginaire. Référence partagée [1], annexe "
            r"page~\pageref{citation:1}.\\" + "\n"
        )
    sections = [
        (
            "Jeanne Fictive -- notes longues",
            "person:jeanne",
            r"Un événement individuel documenté.\sourcecall"
            + r"\footnote{Note longue fictive. "
            + ("Cette précision documentaire reste lisible au bas de la page. " * 18)
            + "}",
        ),
        (
            "Descendance -- branche de Camille",
            "person:child",
            r"Camille Exemple, génération +1. Couple central : page~\pageref{family:0}. Ascendance commune : page~\pageref{ancestor:1}.",
        ),
        (
            "Famille monoparentale du parcours",
            "family:single",
            "Un parent connu et un enfant. Aucun second parent n'est ajouté. Ce cas est autorisé dans le parcours, distinct du couple central incomplet qui est refusé.",
        ),
        (
            "Plusieurs fiches sur une page",
            "profiles:compact",
            r"\subsection*{Personne fictive A}Un événement professionnel.\sourcecall\subsection*{Personne fictive B}Un événement de résidence.\sourcecall\subsection*{Personne fictive C}Une note conservée dans son contexte.",
        ),
        (
            "Photographie importante",
            "media:featured",
            r"\fbox{\parbox[c][170mm][c]{.94\linewidth}{\centering Emplacement d'une photographie fictive BOOK\_FEATURED.\\ Reproduction principale unique.}}",
        ),
        (
            "Annexe documentaire",
            "citation:1",
            r"[1] Registre entièrement fictif. Citation C0001, source S0001, dépôt R0001, cote EX-1, page 42.\par URL imprimée : \url{https://example.org/archive/registre-fictif/document-0001/page-0042?mode=consultation&language=fr}\par\fbox{\parbox[c][80mm][c]{.94\linewidth}{\centering Document justificatif fictif, reproduction unique.}}",
        ),
        (
            "Autre citation du même document",
            "citation:2",
            r"[2] Citation C0002 de la source S0001. Le document est reproduit uniquement page~\pageref{citation:1}. La citation conserve son identité.",
        ),
        (
            "Caractères et textes difficiles",
            "escaping",
            r"Émile \& Jeanne : 50\%, identifiant A\_B, cote \#42, coût 10\$, accolades \{texte\}, barre \textbackslash{}input.\par Ces caractères sont du texte, pas des commandes issues d'une note.\par\url{https://example.org/une-reference-documentaire-avec-un-chemin-tres-long/archives/registre/folio/000042}",
        ),
        (
            "Index des personnes",
            "index",
            r"Camille Exemple : \pageref{person:child}.\par Émile Exemple : \pageref{person:emile}.\par Jeanne Fictive : \pageref{person:jeanne}.\par Cet index réduit est construit depuis les identifiants du prototype ; le futur index couvrira toutes les occurrences pertinentes.",
        ),
    ]
    body = HEADER + "".join(rows) + "\\end{longtable}\n"
    for title, label, content in sections:
        body += f"\\newpage\n\\section{{{title}}}\\label{{{label}}}\n{content}\n"
    body += "\\end{document}\n"
    path = ROOT / "layout-spike.tex"
    path.write_text(body, encoding="utf-8")
    print(path)


if __name__ == "__main__":
    build()

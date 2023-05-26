# Projet FishNsharks

Auteurs : Clément Bouvier-Neveu,  Lisa Giordani, Olivier Laurent, Axel Rochel

Date : Mars 2022

## Contexte et problématique

Le but de ce projet est de simuler le comportement d’un banc de poissons dans un environnement avec des prédateurs. La compréhension des mouvements des bancs de poissons, et des essaims en général, est très intéressante car à partir de quelques règles simples il est possible de modéliser des comportements à première vue complexes d’un grand nombre d’individus. Ceci
ouvre deux grands axes d’étude. Tout d’abord la compréhension, modélisation et simulation du comportement de beaucoup d’agents interagissant entre eux. Mais cela donne aussi les clés de la conception pour la robotique en essaim, domaine pour lequel il est très avantageux de pouvoir créer des comportements complexes à partir de beaucoup d’agents très simples.

La robotique en essaim s’inspirant du comportement d’animaux, l’objectif de ce projet est d’implémenter une simulation simplifiée du comportement d’un banc de poissons en interaction avec un prédateur, le requin. Cette simulation doit permettre d’observer qu’un essaim d’agents peut se déplacer dans son environnement tout en évitant des obstacles. Au fur et à mesure
de ce projet, l’environnement simulé devient de plus en plus complexe car nous intégrons des éléments supplémentaires à l’environnement. En partant d’une situation très simple avec juste
des poissons et un requin, nous arrivons à une situation où les poissons peuvent se réfugier contre les requins qui coopèrent mais s’exposent en contrepartie à des goélands.

## Getting started

Pour utiliser ce code, exécutez les commandes suivantes :

1. Créer un environnement virtuel : `python -m venv .projectenv`
2. Activer l'environment : `source .projectenv/bin/activate`
3. Installer les prérequis : `pip3 install -r requirements.txt`
4. Se déplacer dans le dossier `fishnshark` et lancer la commande : `python main.py`

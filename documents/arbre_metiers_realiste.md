# Arbre d'évolution des métiers (réaliste)

Document en **Markdown**, mis à jour à chaque nouvelle demande.

## 1. Présentation générale

Cet arbre représente l'évolution réaliste des métiers dans un jeu de crafting, sans éléments fantastiques et sans orientation survie/colonisation. Il sert de base pour structurer la progression du joueur.

Structure des niveaux :

* **N1 : Métier de base**
* **N2 : Spécialisation intermédiaire**
* **N3 : Expertise avancée**

---

## 2. Arbre d'évolution des métiers

### ⛏️ Minerai & Pierre

**N1 – Mineur**

* N2 : Mineur de surface
* N2 : Mineur de roche dure
* N2 : Carrier

  * N3 : Métallurgiste
  * N3 : Forgeron
  * N3 : Armurier / Fabricant d'outils spécialisés
  * N3 : Tailleur de pierre

---

### 🌲 Bois

**N1 – Bûcheron**

* N2 : Débardeur
* N2 : Scieur

  * N3 : Menuisier
  * N3 : Charpentier
  * N3 : Ébéniste

---

### 🌱 Plantes

**N1 – Herboriste**

* N2 : Cultivateur de plantes spécialisées (lin, coton, médicinales)
* N2 : Jardinier

  * N3 : Tisserand
  * N3 : Alchimiste (teintures, huiles, onguents)

---

### 🐄 Animaux

**N1 – Chasseur / Éleveur**

* N2 : Boucher
* N2 : Tanneur
* N2 : Berger

  * N3 : Sellier / Maroquinier
  * N3 : Fourreur (réaliste : vêtements, sacs)

---

### 🌾 Agriculture

**N1 – Fermier**

* N2 : Céréalier
* N2 : Horticulteur
* N2 : Apiculteur

  * N3 : Meunier
  * N3 : Brasseur / Distillateur
  * N3 : Cuisinier spécialisé

---

### 🎣 Ressources aquatiques

**N1 – Pêcheur**

* N2 : Pêcheur spécialisé (côtier / intérieur)
* N2 : Conservateur de poissons (fumage, salage)

  * N3 : Poissonnier
  * N3 : Constructeur de filets / Bateaux simples

---

### 📦 Logistique & Construction

**N1 – Transporteur / Manœuvre**

* N2 : Conducteur de bêtes de somme
* N2 : Maçon

  * N3 : Constructeur (bâtiments, infrastructures)
  * N3 : Ingénieur mécanique simple (poulies, moulins, presses)

---

## 3. Version ASCII (compacte)

```
Mineur
 ├─ Minerai (surface)
 ├─ Roche dure
 └─ Carrier
       ├─ Métallurgiste
       ├─ Forgeron
       └─ Tailleur de pierre

Bûcheron
 ├─ Débardeur
 └─ Scieur
       ├─ Menuisier
       ├─ Charpentier
       └─ Ébéniste

Herboriste
 ├─ Cultivateur de fibres
 └─ Jardinier
       ├─ Tisserand
       └─ Alchimiste

Chasseur / Éleveur
 ├─ Boucher
 ├─ Tanneur
 └─ Berger
       ├─ Sellier / Maroquinier
       └─ Fourreur

Fermier
 ├─ Céréalier
 ├─ Horticulteur
 └─ Apiculteur
       ├─ Meunier
       ├─ Brasseur
       └─ Cuisinier avancé

Pêcheur
 ├─ Pêcheur spécialisé
 └─ Conservateur
       ├─ Poissonnier
       └─ Constructeur de filets/bateaux

Transporteur
 ├─ Conducteur de bêtes de somme
 └─ Maçon
       ├─ Constructeur
       └─ Ingénieur mécanique simple
```

---

## 4. Arbre visuel (style skill tree)

Un schéma visuel est ajouté pour représenter les liens entre métiers sous forme de **skill tree**.

```
                [ Mineur ]
        /          |           \
[Mineur surface] [Roche dure] [Carrier]
        \          |           /
        [ Métallurgiste / Forgeron / Tailleur ]

                [ Bûcheron ]
             /               \
      [Débardeur]        [Scieur]
                           |
          [Menuisier – Charpentier – Ébéniste]

                [ Herboriste ]
            /                     \
[Cultivateur fibres]         [Jardinier]
                 \            /
      [Tisserand – Alchimiste]

        [ Chasseur / Éleveur ]
     /          |            \
 [Boucher]   [Tanneur]     [Berger]
                    \
          [Maroquinier – Fourreur]

                [ Fermier ]
   /                 |                \
[Céréalier]   [Horticulteur]     [Apiculteur]
    |              |                 |
[Meunier]    [Cuisinier]      [Brasseur]

                [ Pêcheur ]
         /                   \
[Pêche spécialisé]     [Conservateur]
                             |
                 [Poissonnier – Filets/Bateaux]

        [Transporteur / Manœuvre]
              /                \
[Conducteur bêtes]         [Maçon]
                               |
                   [Constructeur – Ingénieur]
```

---

## 5. Système de progression & compétences

Chaque métier progresse via des **niveaux de maîtrise** :

* **Niveau 1 — Débutant** : accès à 3 actions simples.
* **Niveau 2 — Compagnon** : déblocage de nouvelles ressources et des ateliers de base.
* **Niveau 3 — Artisan** : production spécialisée, économie de matériaux.
* **Niveau 4 — Expert** : pièces complexes, bonus d'efficacité.
* **Niveau 5 — Maître** : objets de haute qualité + réduction des échecs.

Exemples par métier :

* **Mineur** :

  * Nv1 : extraction de pierre
  * Nv2 : minerais communs (fer)
  * Nv3 : minerais semi-rares (cuivre, étain)
  * Nv4 : métaux rares (argent)
  * Nv5 : optimisation (x1.2 ressources)

* **Bûcheron** :

  * Nv1 : petit bois
  * Nv2 : troncs standards
  * Nv3 : essences dures (chêne)
  * Nv4 : bois nobles (noyer)
  * Nv5 : +20% rendement

* **Tisserand** :

  * Nv1 : fil brut
  * Nv2 : tissus simples
  * Nv3 : textiles résistants
  * Nv4 : textiles techniques
  * Nv5 : économie de 30% de fibres

---

## 6. Coûts, ressources et niveaux requis (exemples)

### Métallurgiste

* **Atelier requis** : fourneau basique
* **Coût de déblocage** : 20 minerai de fer + 5 charbon
* **Niveau requis** : Mineur niveau 3
* **Production** : lingots de fer

### Forgeron

* **Atelier requis** : enclume + fourneau
* **Coût de déblocage** : 10 lingots fer + 2 bois dur
* **Niveau requis** : Métallurgiste niveau 2
* **Production** : outils, pièces métalliques

### Charpentier

* **Atelier requis** : établi + scierie
* **Coût de déblocage** : 20 planches + 5 clous
* **Niveau requis** : Bûcheron niveau 2
* **Production** : poutres, structures

### Maroquinier

* **Atelier requis** : établi cuir
* **Coût de déblocage** : 10 peaux tannées
* **Niveau requis** : Tanneur niveau 2
* **Production** : sacs, ceintures, harnais

---

## 7. Ressources naturelles basiques

Liste de ressources réalistes utilisables par les professions.

### 🌑 Ressources minérales

* Pierre
* Pierre dure (granit, basalte)
* Argile
* Sable
* Charbon
* Minerai de fer
* Minerai de cuivre
* Minerai d'étain
* Minerai d'argent
* Calcaire

### 🌲 Ressources forestières

* Bois tendre (pin, sapin)
* Bois dur (chêne, hêtre)
* Bois noble (noyer, acajou)
* Résine
* Écorce
* Branchages
* Fibre végétale brute

### 🌱 Ressources végétales

* Lin
* Coton
* Chanvre
* Plantes médicinales (camomille, thym, sauge)
* Plantes tinctoriales (garance, indigo)
* Herbes aromatiques
* Graines diverses

### 🌾 Ressources agricoles

* Blé
* Orge
* Seigle
* Avoine
* Légumes (carottes, choux, oignons)
* Fruits simples (pommes, baies)

### 🐄 Ressources animales

* Viande
* Peaux brutes
* Laine
* Lait
* Os
* Graisse
* Plumes

### 🎣 Ressources aquatiques

* Poissons
* Coquillages
* Algues
* Eau douce
* Eau salée

### ⛰️ Ressources environnementales diverses

* Boue
* Terre riche
* Gravillons
* Sel
* Récifs / corail mort (usage limité)

---

## 8. Recettes possibles par métier

Voici une première liste de **recettes réalistes** utilisant les ressources naturelles existantes et correspondant aux métiers du document.

### ⛏️ Métallurgiste / Forgeron

**Lingot de fer**

* Ressources : 3 minerai de fer + 1 charbon
* Atelier : Fourneau
* Métier requis : Métallurgiste (N2)

**Outil en fer (marteau, pioche, scie)**

* Ressources : 2 lingots de fer + 1 manche en bois dur
* Atelier : Enclume
* Métier requis : Forgeron (N3)

**Clous**

* Ressources : 1 lingot de fer → 10 clous
* Atelier : Enclume
* Métier requis : Forgeron

---

### 🌲 Menuisier / Charpentier

**Planche de bois**

* Ressources : 1 tronc → 3 planches
* Atelier : Scierie
* Métier requis : Scieur

**Établi de travail**

* Ressources : 4 planches + 6 clous
* Métier requis : Menuisier

**Poutre renforcée**

* Ressources : 2 bois dur + 2 clous
* Métier requis : Charpentier

---

### 🌱 Tisserand / Alchimiste

**Fil de lin**

* Ressources : 3 unités de lin
* Atelier : Rouet
* Métier requis : Tisserand

**Tissu simple**

* Ressources : 3 fils de lin
* Atelier : Métier à tisser
* Métier requis : Tisserand

**Teinture végétale**

* Ressources : 5 plantes tinctoriales + eau
* Atelier : Chaudron
* Métier requis : Alchimiste

---

### 🐄 Maroquinier / Tanneur / Fourreur

**Cuir tanné**

* Ressources : 1 peau brute + 1 sel
* Atelier : Tannière
* Métier requis : Tanneur

**Sac en cuir**

* Ressources : 2 cuir tanné + 1 fil résistant
* Métier requis : Maroquinier

**Cape en fourrure**

* Ressources : 2 peaux épaisses + 1 tissu simple
* Métier requis : Fourreur

---

### 🌾 Fermier / Cuisinier / Meunier

**Farine**

* Ressources : 3 blé
* Atelier : Moulin
* Métier requis : Meunier

**Pain**

* Ressources : 2 farine + 1 eau
* Atelier : Four
* Métier requis : Cuisinier

**Bière**

* Ressources : 3 orge + eau
* Atelier : Brasserie
* Métier requis : Brasseur

---

### 🎣 Poissonnier / Constructeur de filets

**Filet de pêche**

* Ressources : 5 fibres végétales + 2 bois tendre
* Atelier : Établi
* Métier requis : Constructeur de filets

**Poisson préparé**

* Ressources : 1 poisson + sel
* Métier requis : Poissonnier

---

### 🧱 Maçon / Constructeur

**Brique d’argile**

* Ressources : 2 argile + 1 sable
* Atelier : Four à briques
* Métier requis : Maçon

**Mur en pierre**

* Ressources : 6 pierres dures + 2 mortiers
* Atelier : Chantier
* Métier requis : Constructeur

---

## 9. Objets d’atelier & outils : fabrication préalable obligatoire

Dans ce système, **tout objet utilisé comme atelier** (ex. : rouet, fourneau, scierie) doit être **fabriqué préalablement**, car ce ne sont pas des consommables mais des équipements permanents. Leur construction demande des ressources et **des métiers précis**, selon la logique réaliste du crafting.

### 🔧 Principe général

* Un atelier **ne peut pas être utilisé** tant qu’il n’a pas été construit par un métier compétent.
* Chaque atelier possède **un coût en ressources** + **des compétences d’artisans**.
* Certaines structures nécessitent plusieurs métiers pour être construites.

---

## 10. Recettes de fabrication des outils et ateliers

### 🪵 Rouet (outil pour Tisserand)

* **Métiers requis :** Menuisier (structure), Forgeron (axe métallique)
* **Ressources :**

  * 4 bois dur (menuiserie)
  * 1 axe métallique (fer)
  * 2 chevilles ou clous
* **Usage :** permet de transformer le lin/coton → fil

---

### 🔥 Fourneau basique (Métallurgiste)

* **Métiers requis :** Maçon (murets), Menuisier (supports)
* **Ressources :**

  * 8 briques d’argile
  * 4 pierres
  * 2 bois dur (structure)
* **Usage :** fondre minerais → lingots

---

### 🔨 Enclume (Forgeron)

* **Métiers requis :** Métallurgiste
* **Ressources :**

  * 4 lingots de fer
* **Usage :** forge des outils, pièces, clous

---

### 🪚 Scierie manuelle (Scieur)

* **Métiers requis :** Menuisier
* **Ressources :**

  * 4 bois dur
  * 1 lame métallique (forgeron)
* **Usage :** troncs → planches

---

### 🧵 Métier à tisser (Tisserand)

* **Métiers requis :** Menuisier
* **Ressources :**

  * 6 bois tendre
  * 2 barres de fer
* **Usage :** fil → tissu

---

### 🍺 Brasserie simple (Brasseur)

* **Métiers requis :** Menuisier + Alchimiste
* **Ressources :**

  * 4 planches
  * 1 tonneau
  * 1 cuve chauffante
* **Usage :** grains → bière

---

### 🧱 Four à briques (Maçon)

* **Métiers requis :** Maçon
* **Ressources :**

  * 12 pierres
  * 4 briques d’argile
* **Usage :** cuisson des briques

---

### 🧰 Atelier cuir (Tanneur / Maroquinier)

* **Métiers requis :** Menuisier
* **Ressources :**

  * 2 planches
  * 1 surface de travail
* **Usage :** tanner les peaux, fabriquer sacs & harnais

---

### 🐟 Atelier filets & cordages (Constructeur de filets)

* **Métiers requis :** Bûcheron (pour montage), Tisserand (pour fibre)
* **Ressources :**

  * 4 bois tendre
  * 4 fibres végétales
  * 1 élément métallique pour tension
* **Usage :** fibres → filets / cordages

---

## 11. Niveaux d'expérience requis pour crafter chaque élément

Chaque recette, outil ou atelier nécessite un **niveau de métier minimum**, basé sur le système de progression déjà défini (Débutant → Maître). Ci-dessous, les niveaux d’expérience pour chaque élément déjà listé.

### 🔧 Niveaux d’expérience — Ateliers & outils

#### 🪵 Rouet

* **Métiers requis :** Menuisier **N2**, Forgeron **N1**
* **Difficulté :** Intermédiaire

#### 🔥 Fourneau basique

* **Métiers requis :** Maçon **N2**, Menuisier **N1**
* **Difficulté :** Intermédiaire

#### 🔨 Enclume

* **Métiers requis :** Métallurgiste **N3**
* **Difficulté :** Avancée

#### 🪚 Scierie manuelle

* **Métiers requis :** Menuisier **N2**
* **Difficulté :** Intermédiaire

#### 🧵 Métier à tisser

* **Métiers requis :** Menuisier **N2**
* **Difficulté :** Intermédiaire

#### 🍺 Brasserie simple

* **Métiers requis :** Menuisier **N2**, Alchimiste **N1**
* **Difficulté :** Intermédiaire

#### 🧱 Four à briques

* **Métiers requis :** Maçon **N2**
* **Difficulté :** Intermédiaire

#### 🧰 Atelier cuir

* **Métiers requis :** Menuisier **N1**
* **Difficulté :** Basique

#### 🐟 Atelier filets & cordages

* **Métiers requis :** Bûcheron **N1**, Tisserand **N1**
* **Difficulté :** Basique

---

## 11.2 Niveaux — Recettes de production

### Métallurgie & forge

**Lingot de fer** → Métallurgiste **N1**
**Outil en fer** → Forgeron **N2**
**Clous** → Forgeron **N1**

### Travail du bois

**Planche** → Scieur **N1**
**Établi** → Menuisier **N1**
**Poutre renforcée** → Charpentier **N2**

### Textile & alchimie

**Fil de lin** → Tisserand **N1**
**Tissu simple** → Tisserand **N2**
**Teinture végétale** → Alchimiste **N1**

### Cuir & fourrure

**Cuir tanné** → Tanneur **N1**
**Sac en cuir** → Maroquinier **N2**
**Cape en fourrure** → Fourreur **N2**

### Agriculture & cuisine

**Farine** → Meunier **N1**
**Pain** → Cuisinier **N1**
**Bière** → Brasseur **N2**

### Pêche

**Filet de pêche** → Constructeur de filets **N2**
**Poisson préparé** → Poissonnier **N1**

### Construction

**Brique d’argile** → Maçon **N1**
**Mur en pierre** → Constructeur **N2**

---

## 12. Notes

en attente de nouvelles instructions pour étendre, modifier ou détailler l'arbre.

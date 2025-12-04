# 📚 Système de Questions-Réponses pour manuels de procédures

Un système intelligent de recherche et de question-réponse basé sur l'IA pour interroger des manuels de procédures générales. Utilise la génération augmentée par retrieval (RAG) avec une mémoire conversationnelle.

## 🎯 Fonctionnalités

- ✅ **Conversion de documents** - Supporte les fichiers Word (.docx) et PDF (.pdf)
- ✅ **Chunking intelligent** - Utilise le chunking hybride de Docling
- ✅ **Embeddings sémantiques** - Modèle mxbai-embed-large d'Ollama
- ✅ **Base de données vectorielle** - Stockage avec Chroma
- ✅ **Réponses basées sur le contexte** - Modèle Mistral d'Ollama
- ✅ **Mémoire conversationnelle** - Garde l'historique des questions
- ✅ **Interface utilisateur** - Interface web avec Gradio
- ✅ **Sources citées** - Affiche les documents utilisés pour chaque réponse
- ✅ **Export en PDF/TXT** - Exporte les conversations
- ✅ **Statistiques** - Affiche les statistiques des documents indexés

## 📋 Prérequis

### Logiciels nécessaires
- Python 3.9+
- Ollama (avec les modèles `mxbai-embed-large` et `mistral` installés)

### Installation des dépendances

```bash
pip install langchain-ollama langchain-chroma gradio docling python-docx reportlab
```

## 🚀 Guide de démarrage

### Étape 1: Préparer les documents

1. Placez vos fichiers Word (.docx) ou PDF (.pdf) dans le dossier `docs-procedure/`
2. Exemple de fichiers supportés:
   - `procedure_generale.docx`
   - `securite_operationnelle.docx`
   - `maintenance_etalonage.pdf`
   - `procedure_urgence.docx`
   - `controle_qualite.pdf`

### Étape 2: Créer la base de données vectorielle

```bash
python main.py
```

Ce script va:
1. Convertir tous les documents (Word/PDF) en texte structuré
2. Appliquer le chunking hybride pour créer des chunks sémantiques
3. Générer les embeddings pour chaque chunk
4. Stocker tout dans la base de données Chroma (`./chroma_db/`)

### Étape 3: Lancer l'application

```bash
python app.py
```

L'application sera accessible à: `http://127.0.0.1:7860`

## 📁 Structure du projet

```
final-project/
├── main.py              # Script de préparation de la base de données
├── app.py               # Application web Gradio
├── README.md            # Ce fichier
├── docs-procedure/      # Dossier des documents source (Word / PDF)
│   ├── procedure_generale.docx
│   ├── securite_operationnelle.docx
│   ├── maintenance_etalonage.pdf
│   ├── procedure_urgence.docx
│   └── controle_qualite.pdf
├── exports/             # Dossier des exports PDF/TXT
│   ├── conversation_20251204_123456.pdf
│   └── conversation_20251204_123457.txt
└── chroma_db/           # Base de données vectorielle (créée automatiquement)
    └── chroma.sqlite3
```

## 📊 Export et Statistiques

### Fonctionnalité d'Export

L'application permet d'exporter l'historique de conversation de deux façons:

1. **Export PDF** (si reportlab est installé)
   - Mise en forme professionnelle
   - Distinction des messages (utilisateur en bleu, assistant en vert)
   - Horodatage automatique
   - Stockage dans le dossier `exports/`

2. **Export TXT** (fallback)
   - Format texte brut lisible
   - Pas de dépendance externe
   - Stockage dans le dossier `exports/`

### Fonctionnalité de Statistiques

Le bouton "📊 Voir les statistiques" affiche:
- Nombre total de chunks dans la base de données
- Nombre de documents sources
- Répartition des chunks par document (avec pourcentage)
- Utile pour comprendre la distribution des données

### Exemple d'affichage des statistiques

```
📊 STATISTIQUES SUR LES DOCUMENTS

Nombre total de chunks: 1250
Nombre de documents sources: 5

Répartition par document:
• procedure_generale.docx: 350 chunks (28.0%)
• maintenance_etalonage.pdf: 280 chunks (22.4%)
• controle_qualite.pdf: 260 chunks (20.8%)
• securite_operationnelle.docx: 220 chunks (17.6%)
• procedure_urgence.docx: 140 chunks (11.2%)
```

## 🔧 Configuration

### Variables d'environnement Ollama

Assurez-vous que Ollama est en cours d'exécution avec les modèles requis:

```bash
# Installer les modèles (si pas déjà installés)
ollama pull mxbai-embed-large
ollama pull mistral

# Démarrer Ollama (si pas déjà en cours)
ollama serve
```

### Installation optionnelle de reportlab

Pour obtenir des exports PDF avec une meilleure mise en forme:

```bash
pip install reportlab
```

Si reportlab n'est pas installé, l'export se fera en format TXT.

## 🔄 Flux de fonctionnement

```
1. Document Word → Docling (conversion)
             ↓
2. Texte → HybridChunker (segmentation)
             ↓
3. Chunks → Ollama (embeddings)
             ↓
4. Embeddings → Chroma (indexation vectorielle)
             ↓
5. Requête utilisateur → Recherche vectorielle
             ↓
6. Top-3 chunks + Historique → Prompt Mistral
             ↓
7. Réponse formatée + Sources → Interface Gradio
```

## 📖 Utilisation de l'interface

### Boutons disponibles

- **Rechercher** (bleu) - Soumet la question et reçoit la réponse
- **Effacer** - Efface la question et la réponse actuelles
- **Réinitialiser l'historique** - Supprime tout l'historique de conversation
- **📥 Exporter en PDF/TXT** - Exporte la conversation actuelle en fichier
- **📊 Voir les statistiques** - Affiche les statistiques sur les documents indexés

### Conseils pour de meilleures résultats

1. **Soyez précis** - Posez des questions spécifiques sur les procédures
2. **Utilisez le contexte** - Référencez les conversations précédentes
3. **Consultez les sources** - Vérifiez les documents utilisés pour la réponse
4. **Exportez régulièrement** - Sauvegardez vos conversations importantes

## 🤖 Modèles utilisés

| Composant | Modèle | Fonction |
|-----------|--------|----------|
| Embeddings | `mxbai-embed-large` | Convertir le texte en vecteurs numériques |
| LLM | `mistral` | Générer les réponses |
| Conversion | `Docling` | Extraire le texte des documents (Word / PDF) |
| Chunking | `HybridChunker` | Segmenter les documents intelligemment |

## 🐛 Dépannage

### Erreur: "Connection refused" (Ollama)
```
Solution: Vérifiez que Ollama est en cours d'exécution avec `ollama serve`
```

### Erreur: "No module named 'langchain_chroma'"
```
Solution: Installez langchain-chroma
pip install langchain-chroma
```

### Base de données vide
```
Solution: Assurez-vous que main.py s'est exécuté sans erreurs
Vérifiez que les fichiers .docx sont dans docs-procedure/
```

### Réponses lentes
```
Solution: Ottimez les paramètres:
- Réduisez k dans search_kwargs
- Réduisez la taille des chunks
- Vérifiez les ressources système
```

## 📚 Améliorations possibles

- [x] Support de formats supplémentaires (PDF, TXT, etc.)
- [x] Statistiques sur les documents
- [x] Export des réponses en PDF
- [ ] Filtrage par document source
- [ ] Interface multilingue
- [ ] Authentification utilisateur
- [ ] Historique persistant en base de données
- [ ] Intégration avec d'autres modèles LLM

## 📝 Notes techniques

### Architecture RAG
- **Retriever**: Recherche sémantique via embeddings vectoriels
- **Augmentation**: Récupération des top-3 chunks pertinents
- **Generation**: Utilisation du contexte pour générer les réponses

### Gestion de la mémoire
- Les 4 derniers messages sont conservés dans le contexte
- L'historique est stocké en mémoire (réinitialisation à chaque redémarrage)
- Pas de persistance de l'historique entre les sessions

## 📄 Licence

Ce projet est fourni à des fins éducatives.

## 👥 Auteur

Projet de Question-Réponse sur les manuels de procédures
Date: Décembre 2025

## 📞 Support

Pour toute question ou problème:
1. Vérifiez la section "Dépannage" ci-dessus
2. Consultez les logs d'Ollama
3. Assurez-vous que tous les prérequis sont installés

## 🧭 Nouveau prompt (template)

Le système utilise un template de prompt adapté pour interroger des manuels de procédures. Principales consignes:

- Utiliser uniquement le contexte fourni (extraits/paragraphes/sections).
- Ne pas inventer d'information ; si manquant, indiquer clairement que l'information n'a pas été trouvée.
- Pour les procédures, fournir une liste numérotée d'étapes.
- Toujours ajouter une section "Sources" avec les fichiers ou sections consultés.
- Indiquer un niveau de confiance (Élevé / Moyen / Faible) et la raison.
- Poser jusqu'à 2 questions de clarification si la requête est ambigüe.

Exemple de portion du prompt utilisée par l'application:

```
Tu es un assistant expert chargé d'interroger un manuel de procédures.
Utilise uniquement le CONTEXTE fourni pour répondre (extraits, paragraphes, sections).
Ne devine pas en dehors du contexte ; si l'information n'apparaît pas dans le contexte, indique clairement
que l'information n'a pas été trouvée et propose des termes ou sections à rechercher.

Consignes de réponse :
- Résumé concis (1-2 phrases) de la réponse.
- Si la question demande une procédure, fournis une liste NUMÉROTÉE des étapes à suivre.
- Après la réponse, ajoute une section "Sources" listant les fichiers/sections utilisés.
- Indique un court niveau de confiance (Élevé / Moyen / Faible) et la raison.
- Si la question est ambiguë ou il manque des précisions, pose jusqu'à 2 questions de clarification.
- Réponds en français.
```

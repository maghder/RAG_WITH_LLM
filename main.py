# ============================================================================
# Script de Préparation de la Base de Données Vectorielle
# ============================================================================
# Ce script:
# 1. Convertit les documents Word et PDF en texte structuré (Docling)
# 2. Applique le chunking hybride pour créer des chunks sémantiques
# 3. Génère les embeddings avec le modèle mxbai-embed-large (Ollama)
# 4. Stocke les chunks dans une base de données Chroma
# ============================================================================

from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from pathlib import Path

# Dossier contenant les documents à traiter
docs_folder = Path(r"docs-procedure")

# Initialiser les composants
converter = DocumentConverter()
chunker = HybridChunker()
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# ============================================================================
# TRAITEMENT DES DOCUMENTS
# ============================================================================

# Stocker tous les chunks et leurs métadonnées
all_chunks = []
chunk_metadatas = []

# Traiter chaque document du dossier (Word et PDF)
for doc_file in docs_folder.glob("*"):
    if doc_file.suffix.lower() not in [".docx", ".pdf"]:
        continue
    
    print(f"Traitement: {doc_file.name}")
    
    try:
        # Convertir le document avec Docling (supporte Word et PDF)
        doc = converter.convert(str(doc_file)).document
        
        # Appliquer le chunking hybride
        chunks = list(chunker.chunk(doc))
        print(f"  → {len(chunks)} chunks créés")
        
        # Ajouter les chunks avec leurs métadonnées
        for chunk in chunks:
            all_chunks.append(chunk.text)
            chunk_metadatas.append({"source": doc_file.name})
    except Exception as e:
        print(f"Erreur lors du traitement de {doc_file.name}: {e}")
        import traceback
        traceback.print_exc()

print(f"\nNombre total de chunks créés: {len(all_chunks)}")

# Vérifier que des chunks ont été créés
if not all_chunks:
    print("Erreur: Aucun chunk n'a pu être créé à partir des documents.")
    print("Vérifiez que:")
    print("  1. Le dossier 'docs-procedure' contient des fichiers .docx ou .pdf")
    print("  2. Les documents ne sont pas vides")
    print("  3. Docling peut convertir les documents correctement")
    exit(1)

# ============================================================================
# CRÉATION DE LA BASE DE DONNÉES VECTORIELLE
# ============================================================================

print("Création de la base de données vectorielle avec embeddings...")
vector_db = Chroma.from_texts(
    texts=all_chunks,
    embedding=embeddings,
    metadatas=chunk_metadatas,
    persist_directory="./chroma_db",
    collection_name="documents"
)

print("Base de données vectorielle créée avec succès!")
print(f"Stockage de {len(all_chunks)} chunks dans la base de données Chroma.")

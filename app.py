# ============================================================================
# Application de Questions-Réponses pour manuels de procédures
# ============================================================================
# Utilise Gradio pour l'interface utilisateur
# Intègre Ollama pour les embeddings et le modèle LLM
# Utilise Chroma comme base de données vectorielle
# ============================================================================

import gradio as gr
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from datetime import datetime
from pathlib import Path
import json
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Historique de la conversation pour la mémoire contextuelle
conversation_history = []

# Dossier pour les exports
export_folder = Path("exports")
export_folder.mkdir(exist_ok=True)

# ============================================================================
# INITIALISATION DES COMPOSANTS
# ============================================================================

# Initialiser les embeddings avec le modèle mxbai-embed-large
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Charger la base de données vectorielle Chroma existante
vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="documents"
)

# Initialiser le modèle LLM Mistral
llm = OllamaLLM(model="mistral")

# ============================================================================
# CONFIGURATION DU PROMPT ET DE LA CHAÎNE RAG
# ============================================================================

# Créer le modèle de prompt avec historique de conversation
prompt = ChatPromptTemplate.from_template(
    """Tu es un assistant expert chargé d'interroger un manuel de procédures.
Utilise uniquement le CONTEXTE fourni pour répondre (extraits, paragraphes, sections).
Ne devine pas en dehors du contexte ; si l'information n'apparaît pas dans le contexte, indique clairement
que l'information n'a pas été trouvée et propose des termes ou sections à rechercher.

Consignes de réponse :
- Résumé concis (4-6 phrases) de la réponse.
- Si la question demande une procédure, fournis une liste NUMÉROTÉE des étapes à suivre.
- Après la réponse, ajoute une section "Sources" listant les fichiers/sections utilisés (format : `NomFichier: [page/section]` si disponible).
- Indique un court niveau de confiance (Élevé / Moyen / Faible) et la raison.
- Si la question est ambiguë ou il manque des précisions, pose jusqu'à 2 questions de clarification.
- Réponds en français.

Contexte: {context}

Historique de conversation:
{history}

Question: {question}

Réponse:"""
)

# Initialiser le récupérateur avec top-3 résultats similaires
retriever = vector_db.as_retriever(search_kwargs={"k": 5})

# Fonction pour formater les documents récupérés
def format_docs(docs):
    """Joindre les contenus des documents avec séparation"""
    return "\n\n".join(doc.page_content for doc in docs)

# Fonction pour formater l'historique de conversation
def format_history():
    """Convertir l'historique en chaîne lisible pour le prompt"""
    if not conversation_history:
        return "Aucune conversation précédente."
    history_text = ""
    # Garder les 4 derniers messages pour le contexte
    for msg in conversation_history[-4:]:
        if isinstance(msg, dict):
            role = msg["role"]
            content = msg["content"]
            history_text += f"{role}: {content}\n"
    return history_text

# Créer la chaîne RAG (Retrieval-Augmented Generation)
rag_chain = (
    {
        "context": retriever | format_docs,
        "history": lambda x: format_history(),
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

# ============================================================================
# FONCTIONS DE TRAITEMENT DES REQUÊTES
# ============================================================================

def query_documents(question):
    """
    Traiter une question et retourner la réponse avec les sources
    
    Args:
        question (str): La question posée par l'utilisateur
        
    Returns:
        str: La réponse formatée avec les sources utilisées
    """
    try:
        # Obtenir la réponse de la chaîne RAG
        answer = rag_chain.invoke(question)
        
        # Sauvegarder dans l'historique de conversation
        conversation_history.append({"role": "Utilisateur", "content": question})
        conversation_history.append({"role": "Assistant", "content": answer})
        
        # Récupérer les documents pertinents (sources)
        docs = retriever.invoke(question)
        sources = list(set([doc.metadata.get("source", "Unknown") for doc in docs]))
        
        # Formater la réponse avec les sources
        response = f"{answer}\n\n---\n\n📚 **Sources utilisées:**\n"
        for source in sources:
            response += f"• {source}\n"
        
        return response
    except Exception as e:
        return f"Erreur: {str(e)}"


def export_to_pdf():
    """
    Exporter la conversation actuelle en PDF
    """
    try:
        if not conversation_history:
            return "Aucune conversation à exporter."
        
        if not REPORTLAB_AVAILABLE:
            # Utiliser un format texte simple si reportlab n'est pas disponible
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"exports/conversation_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("EXPORT DE CONVERSATION - MANUEL DE PROCÉDURES\n")
                f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for msg in conversation_history:
                    role = msg.get("role", "Unknown")
                    content = msg.get("content", "")
                    f.write(f"\n{role}:\n")
                    f.write("-" * 40 + "\n")
                    f.write(content)
                    f.write("\n")
            
            return f"✅ Conversation exportée en texte: {filename}"
        
        # Exportation PDF avec reportlab
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.units import inch
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/conversation_{timestamp}.pdf"
        
        # Créer le document PDF
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # En-tête
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            alignment=1
        )
        
        story.append(Paragraph("EXPORT DE CONVERSATION", title_style))
        story.append(Paragraph("Système de Questions-Réponses sur les manuels de procédures", styles['Normal']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        # Contenu de la conversation
        for msg in conversation_history:
            role = msg.get("role", "Unknown")
            content = msg.get("content", "")
            
            # Style basé sur le rôle
            if role == "Utilisateur":
                msg_style = ParagraphStyle(
                    'UserMessage',
                    parent=styles['Normal'],
                    textColor=colors.HexColor('#0066cc'),
                    fontSize=10,
                    spaceAfter=8,
                    leftIndent=0.2*inch
                )
            else:
                msg_style = ParagraphStyle(
                    'AssistantMessage',
                    parent=styles['Normal'],
                    textColor=colors.HexColor('#006600'),
                    fontSize=10,
                    spaceAfter=8,
                    leftIndent=0.2*inch
                )
            
            story.append(Paragraph(f"<b>{role}:</b>", msg_style))
            # Tronquer les réponses très longues
            content_short = content[:500] + "..." if len(content) > 500 else content
            story.append(Paragraph(content_short, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Générer le PDF
        doc.build(story)
        return f"✅ Conversation exportée en PDF: {filename}"
    
    except Exception as e:
        return f"❌ Erreur lors de l'export: {str(e)}"


def get_document_statistics():
    """
    Récupérer les statistiques sur les documents dans la base de données
    """
    try:
        # Récupérer tous les documents de la collection
        collection = vector_db.get()
        
        if not collection or not collection.get('ids'):
            return "Aucun document dans la base de données."
        
        # Compter les documents par source
        sources = {}
        metadatas = collection.get('metadatas', [])
        
        for metadata in metadatas:
            source = metadata.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        # Construire le rapport de statistiques
        stats_text = "📊 **STATISTIQUES SUR LES DOCUMENTS**\n\n"
        stats_text += f"Nombre total de chunks: {len(collection.get('ids', []))}\n"
        stats_text += f"Nombre de documents sources: {len(sources)}\n\n"
        stats_text += "**Répartition par document:**\n"
        
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(collection.get('ids', []))) * 100
            stats_text += f"• {source}: {count} chunks ({percentage:.1f}%)\n"
        
        return stats_text
    
    except Exception as e:
        return f"Erreur lors de la récupération des statistiques: {str(e)}"

# ============================================================================
# INTERFACE UTILISATEUR GRADIO
# ============================================================================

# Créer l'interface avec Gradio
with gr.Blocks(title="Système QA - Procédures d'Archivage") as demo:
    gr.Markdown("# 📚 Système de Questions-Réponses sur les Procédures d'Archivage")
    gr.Markdown("Posez des questions sur les documents d'archivage. Le système se souviendra de vos questions précédentes.")
    
    # Section pour la saisie de la question
    with gr.Row():
        question_input = gr.Textbox(
            label="Votre Question",
            placeholder="Tapez votre question ici...",
            lines=3
        )
    
    # Section pour les boutons d'action
    with gr.Row():
        submit_btn = gr.Button("Rechercher", variant="primary")
        clear_btn = gr.Button("Effacer")
        reset_history_btn = gr.Button("Réinitialiser l'historique")
    
    # Section pour l'affichage de la réponse
    with gr.Row():
        answer_output = gr.Textbox(
            label="Réponse",
            lines=8,
            interactive=False
        )
    
    # Section pour les fonctionnalités supplémentaires
    with gr.Row():
        export_btn = gr.Button("📥 Exporter en PDF/TXT", variant="secondary")
        stats_btn = gr.Button("📊 Voir les statistiques", variant="secondary")
    
    with gr.Row():
        stats_output = gr.Textbox(
            label="Statistiques / Export",
            lines=6,
            interactive=False
        )
    
    # Fonction pour réinitialiser l'historique
    def reset_history():
        """Effacer l'historique de conversation"""
        conversation_history.clear()
        return ("", "")
    
    # Événements des boutons
    submit_btn.click(
        fn=query_documents,
        inputs=question_input,
        outputs=answer_output
    )
    
    clear_btn.click(
        fn=lambda: ("", ""),
        outputs=[question_input, answer_output]
    )
    
    reset_history_btn.click(
        fn=reset_history,
        outputs=[question_input, answer_output]
    )
    
    export_btn.click(
        fn=export_to_pdf,
        outputs=stats_output
    )
    
    stats_btn.click(
        fn=get_document_statistics,
        outputs=stats_output
    )

# ============================================================================
# LANCEMENT DE L'APPLICATION
# ============================================================================

if __name__ == "__main__":
    # Lancer l'application Gradio
    # Accessible à http://127.0.0.1:7860
    demo.launch(server_name="127.0.0.1", server_port=7860)

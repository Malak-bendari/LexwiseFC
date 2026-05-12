import json
import logging

from flask import current_app
from google import genai
from google.genai import types

from app.database.db import db
from app.models.user import User
from app.models.ai_profile import AIProfile
from app.services.finance_service import FinanceService
from app.services.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es LexWise, un coach financier personnel intelligent et bienveillant.
Tu parles en français de manière claire, encourageante et accessible.

Ton rôle :
- Analyser la situation financière de l'utilisateur à partir de ses données réelles.
- Donner des conseils personnalisés, concrets et actionnables.
- Alerter sur les risques financiers détectés.
- Encourager de bonnes habitudes financières.

Règles :
- Réponds toujours en français.
- Sois concis mais complet (2 à 5 phrases maximum).
- Utilise les données financières fournies dans le contexte pour personnaliser ta réponse.
- Ne fabrique jamais de chiffres. Utilise uniquement les données du contexte.
- Adapte ton ton au style de coaching préféré de l'utilisateur (motivant, strict, ou équilibré).
"""


class AIService:

    @staticmethod
    def _get_gemma_client():
        """Create a google-genai client using the configured API key."""
        api_key = current_app.config.get("GEMINI_API_KEY", "")
        if not api_key:
            return None
        return genai.Client(api_key=api_key)

    @staticmethod
    def build_financial_context(user_id):
        """Gather the user's financial data into a structured context dict."""
        user = db.session.get(User, user_id)
        ai_profile = AIProfile.query.filter_by(user_id=user_id).first()

        summary = FinanceService.calculate_monthly_summary(user_id)
        risks = FinanceService.detect_financial_risks(user_id)
        recommendations = RecommendationEngine.generate_recommendations(user_id)

        return {
            "user": {
                "name": user.name if user else "User",
                "plan": user.plan if user else "go",
                "monthly_income": user.monthly_income if user else 0
            },
            "ai_profile": {
                "financial_goal": ai_profile.financial_goal if ai_profile else None,
                "risk_level": ai_profile.risk_level if ai_profile else "medium",
                "coaching_style": ai_profile.preferred_coaching_style if ai_profile else "balanced"
            },
            "summary": summary,
            "risks": risks,
            "recommendations": recommendations
        }

    @staticmethod
    def _format_context_for_prompt(context):
        """Convert the financial context dict into a readable string for the LLM."""
        user = context["user"]
        profile = context["ai_profile"]
        summary = context["summary"]
        risks = context["risks"]

        lines = [
            f"Utilisateur : {user['name']}",
            f"Plan : {user['plan']}",
            f"Revenu mensuel déclaré : {user['monthly_income']}€",
            f"Objectif financier : {profile['financial_goal'] or 'Non défini'}",
            f"Niveau de risque : {profile['risk_level']}",
            f"Style de coaching : {profile['coaching_style']}",
            "",
            f"--- Résumé du mois ({summary['month']}) ---",
            f"Revenus totaux : {summary['total_income']}€",
            f"Dépenses totales : {summary['total_expenses']}€",
            f"Reste : {summary['remaining']}€",
            f"Taux d'épargne : {summary['savings_rate']}%",
        ]

        if summary["expenses_by_category"]:
            lines.append("")
            lines.append("Dépenses par catégorie :")
            for cat, amount in summary["expenses_by_category"].items():
                lines.append(f"  - {cat} : {amount}€")

        if risks:
            lines.append("")
            lines.append("Risques détectés :")
            for risk in risks:
                lines.append(f"  - [{risk['level'].upper()}] {risk['message']}")

        return "\n".join(lines)

    @staticmethod
    def _call_gemma(user_message, context):
        """
        Call the Gemma model via google-genai.
        Falls back to a rule-based response if the API key is missing or the call fails.
        """
        client = AIService._get_gemma_client()

        if client is None:
            logger.warning("GEMINI_API_KEY not configured — falling back to rule-based response.")
            return None

        context_text = AIService._format_context_for_prompt(context)
        full_user_message = (
            f"Voici les données financières de l'utilisateur :\n\n"
            f"{context_text}\n\n"
            f"---\n\n"
            f"{user_message}"
        )

        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=full_user_message)],
                ),
            ]

            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=500,
            )

            response = client.models.generate_content(
                model="gemma-4-26b-a4b-it",
                contents=contents,
                config=config,
            )

            return response.text

        except Exception as e:
            logger.error(f"Gemma API call failed: {e}")
            return None

    @staticmethod
    def _fallback_coach_message(context):
        """Rule-based fallback when the AI model is unavailable."""
        user_name = context["user"]["name"]
        summary = context["summary"]
        recommendations = context["recommendations"]

        if summary["total_income"] == 0:
            return (
                f"Bonjour {user_name}, commence par ajouter tes revenus "
                f"et tes dépenses pour que je puisse te donner une analyse personnalisée."
            )

        main_rec = (
            recommendations[0]["message"]
            if recommendations
            else "Continue à suivre tes dépenses régulièrement."
        )

        return (
            f"Bonjour {user_name}, ce mois-ci tu as gagné {summary['total_income']}€ "
            f"et dépensé {summary['total_expenses']}€. "
            f"Il te reste {summary['remaining']}€. "
            f"Ton taux d'épargne est de {summary['savings_rate']}%. "
            f"Conseil principal : {main_rec}"
        )

    @staticmethod
    def generate_coach_message(user_id):
        """Generate a personalised coaching message using Gemma (or fallback)."""
        context = AIService.build_financial_context(user_id)

        ai_message = AIService._call_gemma(
            "Donne-moi un bilan personnalisé de ma situation financière ce mois-ci "
            "avec un conseil principal.",
            context
        )

        if ai_message is None:
            ai_message = AIService._fallback_coach_message(context)

        return {
            "coach": "LexWise",
            "message": ai_message,
            "context": context
        }

    @staticmethod
    def answer_user_question(user_id, question):
        """Answer a user's financial question using Gemma (or fallback)."""
        context = AIService.build_financial_context(user_id)

        ai_answer = AIService._call_gemma(
            f"L'utilisateur te pose la question suivante : {question}",
            context
        )

        if ai_answer is None:
            ai_answer = AIService._fallback_answer(user_id, question, context)

        return {"answer": ai_answer}

    @staticmethod
    def _fallback_answer(user_id, question, context):
        """Rule-based fallback for answering questions."""
        summary = context["summary"]
        question_lower = question.lower()

        if "dépense" in question_lower or "depense" in question_lower:
            return (
                f"Ce mois-ci, tes dépenses totales sont de {summary['total_expenses']}€. "
                f"Voici la répartition : {summary['expenses_by_category']}."
            )

        if "épargne" in question_lower or "epargne" in question_lower:
            return (
                f"Ton taux d'épargne actuel est de {summary['savings_rate']}%. "
                f"L'objectif recommandé est d'atteindre au moins 10% à 20%."
            )

        if "budget" in question_lower:
            budget_status = FinanceService.analyze_budget_status(user_id)
            return f"Voici l'état de tes budgets : {budget_status}"

        return AIService._fallback_coach_message(context)
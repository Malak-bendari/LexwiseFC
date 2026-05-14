import os
from openai import OpenAI
from dotenv import load_dotenv
import re
import json

load_dotenv()

class GrokService:
    def __init__(self):
        self.api_key = os.environ.get('GROQ_API_KEY')
        self.client = None
        self.model = "llama-3.3-70b-versatile"
        
        if self.api_key:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.groq.com/openai/v1",
                )
                print("✅ Groq API initialized successfully")
            except Exception as e:
                print(f"❌ Groq API init error: {e}")
        else:
            print("❌ GROQ_API_KEY not found in environment")
    
    def get_system_prompt(self, profile_type, language):
        """Professional yet friendly system prompt with formatting rules"""
        
        base_prompt = """You are Lex, a professional AI assistant for LexWise platform, helping freelancers and investors.
    Your role is to help with business, finance, freelancing, investments, and legal contracts.
    Do NOT tell jokes, do NOT engage in small talk yet be friendly when talking to others even if they're wrong try to explain gently, wisely and professionally.

    TONE: Professional but warm. Think of a friendly financial advisor or business mentor. Be knowledgeable, helpful, and approachable. Even when correcting someone, be kind and constructive.

    CRITICAL FORMATTING RULES (MUST FOLLOW):
    - NEVER put spaces before or after commas (write "business, finance" not "business , finance")
    - NEVER put spaces before periods
    - Use line breaks between different sections
    - Use **bold** for important terms (like **Score: 85/100**)
    - Use bullet points with • or - for lists (each on a new line)

    FORMAT: Write in short, natural sentences. Use line breaks to separate thoughts, but keep it flowing like a natural conversation.

    EXAMPLE (good):
    "Great question! To improve your project score, I'd focus on three things:

    • First, clearly define the problem you're solving
    • Second, add specific technical details
    • Third, include market research

    **Your current score would be around 72/100**. Want me to review your actual description?"

    EXAMPLE (bad - too robotic):
    "Introduction: I am Lex... Services: Business planning, Financial analysis..."

    RULES:
    - Be direct and helpful
    - Ask clarifying questions when needed
    - Use emojis sparingly (🚀 for projects, 💡 for tips, 💰 for investments, ⚖️ for contracts)
    - Keep paragraphs short (2-3 sentences)
    - Sound like a knowledgeable professional, not a robot
    - When someone is wrong, explain why gently and offer the correct information

    REMEMBER: Write "business, finance, contracts" NOT "business , finance , contracts" """

        if language == 'fr':
            return base_prompt + """
    EXEMPLE en français:
    "Bonne question ! Pour améliorer votre score, je vous recommande trois choses :

    • Définissez clairement le problème
    • Ajoutez des détails techniques
    • Incluez une étude de marché

    **Votre score actuel serait d'environ 72/100**. Voulez-vous que je révise votre description ?"

    RÈGLES IMPORTANTES:
    - Jamais d'espace avant les virgules (écrivez "affaires, finance" pas "affaires , finance")
    - Jamais d'espace avant les points
    - Utilisez • pour les listes
    - Utilisez **gras** pour les termes importants
    - Soyez gentil même quand quelqu'un a tort, expliquez avec douceur et professionnalisme"""

        return base_prompt
    
    def format_response(self, text):
        """Clean and format the response for better readability"""
        if not text:
            return text
        
        # Ensure double line breaks before numbered lists
        text = re.sub(r'(\d+\.)', r'\n\n\1', text)
        
        # Ensure line breaks before bullet points
        text = re.sub(r'([^•\n])(•)', r'\1\n\2', text)
        
        # Ensure line breaks after section headers
        text = re.sub(r'(\*\*[^*]+\*\*)', r'\n\1\n', text)
        
        # Remove multiple consecutive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Add space after bullet points if missing
        text = re.sub(r'•([^ ])', r'• \1', text)
        
        return text.strip()
    
    def chat(self, message, profile_type, language='en'):
        """Send a message and get AI response"""
        
        if not self.client:
            return self.get_fallback(message, profile_type, language)
        
        try:
            print(f"🔄 Sending to Groq: {message[:50]}...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt(profile_type, language)},
                    {"role": "user", "content": message}
                ],
                temperature=0.6,
                max_tokens=500,
            )
            
            reply = response.choices[0].message.content
            formatted_reply = self.format_response(reply)
            print(f"✅ Got response from Groq")
            return formatted_reply
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return self.get_fallback(message, profile_type, language)
    
    def get_fallback(self, message, profile_type, language='en'):
        """Professional fallback responses"""
        if language == 'fr':
            return "📊 **Je suis Lex**\n\nJe peux vous aider à:\n• Évaluer vos idées de projets\n• Trouver des investisseurs\n• Analyser des contrats\n\nDécrivez-moi votre projet !"
        else:
            return "📊 **I'm Lex**\n\nI can help you with:\n• Score your project ideas\n• Find investors\n• Review contracts\n\nDescribe your project to me!"

    # ========== NEW: Analyze Project with AI ==========
    def analyze_project(self, title, description, category, budget):
        """Use AI to analyze project originality and market potential"""
        
        if not self.client:
            return self._get_fallback_project_analysis(title, description)
        
        try:
            print(f"🤖 Analyzing project: {title[:50]}...")
            
            prompt = f"""You are an expert startup investor and business analyst. Analyze this project idea and return ONLY a JSON object.

PROJECT TITLE: {title}
DESCRIPTION: {description[:2500]}
CATEGORY: {category if category else 'Not specified'}
BUDGET: {budget if budget else 'Not specified'}

Evaluate based on these criteria:
1. ORIGINALITY (0-100): How unique and innovative is this idea? Is it copy-paste or truly novel?
2. MARKET POTENTIAL (0-100): Is there a real market need? Size of opportunity?
3. VIABILITY (0-100): Can this actually be built and succeed?
4. COMPLETENESS (0-100): How well is the idea described? Clear value proposition?

Return ONLY this JSON structure (no other text):
{{
    "originality_score": 85,
    "market_score": 78,
    "viability_score": 82,
    "completeness_score": 75,
    "final_score": 80,
    "analysis": "Brief 2-3 sentence analysis of the project",
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"],
    "market_insight": "One sentence about market opportunity",
    "investment_readiness": "Early Stage / Seed Ready / Growth Stage"
}}

SCORING GUIDELINES:
- 90-100: Excellent, highly original, clear market need
- 70-89: Good potential, needs some refinement
- 50-69: Average, many competitors or unclear value
- 30-49: Weak, significant issues
- 0-29: Very poor, likely not viable (gibberish, nonsense, or completely unrealistic)

Be HARSH but CONSTRUCTIVE. If the description is nonsense or gibberish (e.g., "asdfasdf", random characters, very short), score below 20 and explain why."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=800,
            )
            
            reply = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', reply, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                # Ensure all fields exist
                result.setdefault('final_score', result.get('originality_score', 50))
                result.setdefault('analysis', 'Analysis complete.')
                result.setdefault('strengths', ['Good potential'])
                result.setdefault('weaknesses', ['Needs more details'])
                result.setdefault('suggestions', ['Add more specific information'])
                result.setdefault('market_insight', 'Market opportunity exists')
                result.setdefault('investment_readiness', 'Early Stage')
                return result
            
            return self._get_fallback_project_analysis(title, description)
            
        except Exception as e:
            print(f"❌ Project analysis error: {e}")
            return self._get_fallback_project_analysis(title, description)
    
    def _get_fallback_project_analysis(self, title, description):
        """Fallback analysis when AI is unavailable"""
        desc_lower = description.lower()
        word_count = len(description.split())
        
        # Check for gibberish
        if word_count < 20 or len(set(description)) < 10:
            return {
                "originality_score": 15,
                "market_score": 10,
                "viability_score": 10,
                "completeness_score": 5,
                "final_score": 10,
                "analysis": "⚠️ This description appears to be invalid or incomplete. Please provide a detailed project description (minimum 100 characters).",
                "strengths": [],
                "weaknesses": ["Invalid or insufficient description"],
                "suggestions": ["Write a detailed description of your project", "Explain the problem you're solving", "Describe your target market"],
                "market_insight": "Cannot evaluate without proper description",
                "investment_readiness": "Not Ready"
            }
        
        # Simple heuristic scoring
        originality = min(80, 40 + (len(set(description.split())) / 10))
        market = min(75, 30 + (word_count / 20))
        viability = min(70, 35 + (word_count / 25))
        completeness = min(70, 20 + (word_count / 15))
        
        final_score = int((originality + market + viability + completeness) / 4)
        
        return {
            "originality_score": int(originality),
            "market_score": int(market),
            "viability_score": int(viability),
            "completeness_score": int(completeness),
            "final_score": final_score,
            "analysis": f"Project has {word_count} words. More detailed descriptions get higher scores. Add 200+ words for better AI analysis.",
            "strengths": ["Project idea submitted successfully"],
            "weaknesses": ["Limited description detail", "Needs more market research", "Lacks competitive analysis"],
            "suggestions": ["Write 200+ words for detailed analysis", "Include competitor research", "Define target audience clearly", "Explain revenue model"],
            "market_insight": "Market analysis requires more information to provide accurate insights.",
            "investment_readiness": "Early Stage - Needs refinement"
        }

    # ========== NEW: Analyze Contract with AI ==========
    def analyze_contract(self, content, title):
        """Use AI to analyze contract fairness and detect risky clauses"""
        
        if not self.client:
            return self._get_fallback_contract_analysis(content)
        
        try:
            print(f"🤖 Analyzing contract: {title[:50]}...")
            
            prompt = f"""You are a legal tech expert specializing in contract analysis. Analyze this contract and return ONLY a JSON object.

CONTRACT TITLE: {title}
CONTRACT CONTENT: {content[:3000]}

Evaluate based on:
1. FAIRNESS SCORE (0-100): How balanced is this contract between both parties?
2. RISK LEVEL: Low/Medium/High/Critical
3. DANGEROUS CLAUSES: Identify specific problematic clauses

Return ONLY this JSON structure:
{{
    "fairness_score": 75,
    "risk_level": "Medium",
    "summary": "2-3 sentence summary of the contract",
    "dangerous_clauses": [
        {{"type": "Indemnification", "severity": "High", "explanation": "Why this is concerning", "suggested_change": "How to fix it"}}
    ],
    "good_clauses": ["Clause 1", "Clause 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "negotiation_script": "Professional negotiation script for the worst clause",
    "should_sign": "Yes with changes / No / Yes after changes"
}}

SCORING GUIDELINES:
- 90-100: Very fair, balanced contract
- 70-89: Generally fair with minor concerns
- 50-69: Several concerning clauses, negotiate
- 30-49: Very one-sided, legal review needed
- 0-29: Extremely unfair, do not sign

If content is gibberish or not a real contract (e.g., "asdfasdf", random text, very short), score below 20 and explain."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=1000,
            )
            
            reply = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', reply, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                result.setdefault('fairness_score', 50)
                result.setdefault('risk_level', 'Medium')
                result.setdefault('dangerous_clauses', [])
                result.setdefault('good_clauses', [])
                result.setdefault('recommendations', ['Review contract carefully'])
                result.setdefault('should_sign', 'Review recommended')
                result.setdefault('negotiation_script', '')
                return result
            
            return self._get_fallback_contract_analysis(content)
            
        except Exception as e:
            print(f"❌ Contract analysis error: {e}")
            return self._get_fallback_contract_analysis(content)
    
    def _get_fallback_contract_analysis(self, content):
        """Fallback contract analysis when AI is unavailable"""
        content_lower = content.lower()
        
        # Check for gibberish
        if len(content) < 100 or len(set(content)) < 20:
            return {
                "fairness_score": 15,
                "risk_level": "Critical",
                "summary": "⚠️ This does not appear to be a valid contract. Please upload a real contract document with proper legal language.",
                "dangerous_clauses": [{"type": "Invalid Document", "severity": "Critical", "explanation": "Content is not a valid contract", "suggested_change": "Upload a real contract document"}],
                "good_clauses": [],
                "recommendations": ["Upload a valid contract document", "Use a standard contract template", "Ensure document has proper legal terms"],
                "negotiation_script": "Cannot generate script for invalid document.",
                "should_sign": "No"
            }
        
        # Check for common contract keywords
        contract_keywords = ['agreement', 'party', 'parties', 'terms', 'conditions', 'shall', 'hereunder', 'witnesseth', 'whereas']
        keyword_count = sum(1 for kw in contract_keywords if kw in content_lower)
        
        if keyword_count < 2:
            return {
                "fairness_score": 25,
                "risk_level": "High",
                "summary": "⚠️ This document lacks standard contract language. May not be a valid legal contract.",
                "dangerous_clauses": [{"type": "Invalid Format", "severity": "High", "explanation": "Missing standard contract terms and legal language", "suggested_change": "Use a standard contract template with proper legal clauses"}],
                "good_clauses": [],
                "recommendations": ["Use a proper contract template", "Include standard legal terms like 'agreement', 'parties'", "Have a legal professional review"],
                "negotiation_script": "Consider using a standard contract template before negotiation.",
                "should_sign": "No"
            }
        
        # Simple fairness calculation
        fair_words = ['mutual', 'both parties', 'reasonable', 'good faith', 'standard', 'industry']
        unfair_words = ['indemnify', 'indemnification', 'non-compete', 'exclusive', 'sole discretion', 'waive', 'irrevocable', 'unlimited']
        
        fair_score = 60
        for word in fair_words:
            if word in content_lower:
                fair_score += 5
        for word in unfair_words:
            if word in content_lower:
                fair_score -= 10
        
        fairness_score = max(0, min(100, fair_score))
        
        risk_level = "Critical" if fairness_score < 30 else "High" if fairness_score < 50 else "Medium" if fairness_score < 75 else "Low"
        
        # Generate a basic negotiation script
        negotiation_script = f"""Dear Counterparty,

I've reviewed the proposed agreement. Based on my analysis (Fairness Score: {fairness_score}/100), I have some concerns about the balance of this contract.

I propose we work together to create a more equitable agreement that protects both parties' interests. 

Please let me know when you're available to discuss the terms.

Best regards,
[Your Name]"""
        
        return {
            "fairness_score": fairness_score,
            "risk_level": risk_level,
            "summary": f"Contract analysis complete. Fairness score: {fairness_score}/100. {len(content)} characters analyzed.",
            "dangerous_clauses": [{"type": "General Review Needed", "severity": risk_level, "explanation": "Review all clauses carefully. Several standard contract terms may need attention.", "suggested_change": "Have a legal professional review the contract"}],
            "good_clauses": ["Standard contract structure detected"],
            "recommendations": ["Review all clauses carefully", "Consider legal consultation for high-value contracts", "Negotiate unclear terms"],
            "negotiation_script": negotiation_script,
            "should_sign": "Review recommended" if fairness_score > 50 else "No - legal review required"
        }

# Create singleton instance
grok_service = GrokService()
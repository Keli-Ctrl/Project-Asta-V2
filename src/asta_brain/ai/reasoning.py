import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from loguru import logger
from src.asta_brain.infrastructure.schemas.market import OHLCV
from src.asta_brain.infrastructure.schemas.trade import TradeSide

class AIReasoningLayer:
    """
    Augments strategy signals with market reasoning using Google's Gemini.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. AI Reasoning Layer will be disabled.")
            self.model = None
        else:
            genai.configure(api_key=self.api_key)
            # Use gemini-1.5-flash for faster response and lower latency
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_signal(
        self, 
        symbol: str, 
        side: TradeSide, 
        market_context: Dict[str, Any],
        recent_ohlcv: list[OHLCV]
    ) -> Dict[str, Any]:
        """
        Takes a signal and market context, returns confidence and reasoning.
        """
        if not self.model:
            return {"confidence_multiplier": 1.0, "reasoning": "AI Layer disabled (no API key)"}

        try:
            # Format data for the prompt
            ohlcv_str = "\n".join([
                f"{d.time}: O={d.open}, H={d.high}, L={d.low}, C={d.close}, V={d.volume}" 
                for d in recent_ohlcv[-10:] # Last 10 candles
            ])
            
            prompt = f"""
            You are an elite institutional quantitative trader. 
            Analyze the following trade signal and market context.
            
            Symbol: {symbol}
            Action: {side}
            
            Recent Market Data (OHLCV):
            {ohlcv_str}
            
            Context:
            {market_context}
            
            Task:
            1. Provide a confidence multiplier (0.0 to 1.0) for this trade based on the context.
            2. Provide a brief professional reasoning for your decision.
            
            Respond strictly in JSON format without markdown code blocks:
            {{
                "confidence_multiplier": float,
                "reasoning": "string"
            }}
            """

            # Use generate_content_async for async support
            response = await self.model.generate_content_async(prompt)
            
            # Extract text and handle potential markdown blocks
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()
                
            result = json.loads(response_text)
            logger.info(f"AI Reasoning for {symbol} {side}: {result['confidence_multiplier']} - {result['reasoning']}")
            return result

        except Exception as e:
            logger.error(f"AI Reasoning failed: {e}")
            return {"confidence_multiplier": 0.5, "reasoning": f"Error in AI analysis: {str(e)}"}

import os
from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic
from loguru import logger
from asta_brain.infrastructure.schemas.market import OHLCV
from asta_brain.infrastructure.schemas.trade import TradeSide

class AIReasoningLayer:
    """
    Augments strategy signals with market reasoning using Anthropic's Claude.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not found. AI Reasoning Layer will be disabled.")
            self.client = None
        else:
            self.client = AsyncAnthropic(api_key=self.api_key)

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
        if not self.client:
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
            
            Respond strictly in JSON format:
            {{
                "confidence_multiplier": float,
                "reasoning": "string"
            }}
            """

            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Basic parsing (in production, use a more robust parser/pydantic)
            import json
            result = json.loads(response.content[0].text)
            logger.info(f"AI Reasoning for {symbol} {side}: {result['confidence_multiplier']} - {result['reasoning']}")
            return result

        except Exception as e:
            logger.error(f"AI Reasoning failed: {e}")
            return {"confidence_multiplier": 0.5, "reasoning": f"Error in AI analysis: {str(e)}"}

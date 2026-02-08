"""
LLM Provider Manager

Handles initialization of different LLM providers based on model selection.
Supports OpenAI, Anthropic, and Google AI models.
API keys are read from environment variables.
"""

import os
from typing import Tuple, Any
from openai import OpenAI


class LLMProvider:
    """Factory for creating appropriate LLM clients"""

    @staticmethod
    def get_client(model: str) -> Tuple[Any, str]:
        """
        Returns appropriate client based on model name

        Args:
            model: Model identifier (e.g., "gpt-4", "claude-3-5-sonnet")

        Returns:
            Tuple of (client, provider_type)
        
        Note:
            API keys must be set in environment variables:
            - OPENAI_API_KEY for OpenAI models
            - ANTHROPIC_API_KEY for Anthropic models
            - GOOGLE_API_KEY for Google models
        """
        model_lower = model.lower()

        # OpenAI models
        if "gpt" in model_lower or "o1" in model_lower:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            return OpenAI(api_key=api_key), "openai"

        # Anthropic models
        elif "claude" in model_lower:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            try:
                import anthropic
                return anthropic.Anthropic(api_key=api_key), "anthropic"
            except ImportError:
                raise ValueError("Anthropic package not installed. Run: pip install anthropic")

        # Google models
        elif "gemini" in model_lower:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                return genai, "google"
            except ImportError:
                raise ValueError("Google AI package not installed. Run: pip install google-generativeai")

        # Mistral, Llama (typically via OpenAI-compatible endpoints)
        elif "mistral" in model_lower or "llama" in model_lower:
            # Many providers offer OpenAI-compatible APIs
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set for Mistral/Llama models")
            return OpenAI(api_key=api_key), "openai"

        else:
            raise ValueError(f"Unknown model provider for: {model}")

    @staticmethod
    def generate_text(
        client: Any,
        provider_type: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text using the appropriate provider's API

        Args:
            client: The provider's client instance
            provider_type: Type of provider ("openai", "anthropic", "google")
            model: Model identifier
            system_prompt: System instructions
            user_prompt: User input
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        try:
            if provider_type == "openai":
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content

            elif provider_type == "anthropic":
                response = client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature
                )
                return response.content[0].text

            elif provider_type == "google":
                model_obj = client.GenerativeModel(model)
                prompt = f"{system_prompt}\n\n{user_prompt}"
                response = model_obj.generate_content(prompt)
                return response.text

            else:
                raise ValueError(f"Unknown provider: {provider_type}")

        except Exception as e:
            return f"Error generating text: {str(e)}"

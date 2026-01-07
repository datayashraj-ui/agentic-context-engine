"""
LLM Manager for Unified AI Workspace

Provides unified interface to multiple local LLM providers:
- Ollama (primary, recommended)
- LM Studio (alternative GUI-based)
- llama.cpp (direct, embedded)

All using OpenAI-compatible API for consistency
"""

from typing import Optional, Dict, Any, List
from enum import Enum
import asyncio

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from openai import OpenAI, AsyncOpenAI
from langchain_openai import ChatOpenAI

from .config import get_config


class LLMProvider(Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    LLAMA_CPP = "llama_cpp"


class LLMManager:
    """
    Unified LLM manager supporting multiple local providers

    Usage:
        llm = LLMManager()
        response = llm.complete("Hello, world!")

        # Or use LangChain-compatible client
        langchain_llm = llm.get_langchain_llm()
        response = langchain_llm.invoke("Hello, world!")
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        config = get_config().llm

        self.provider = LLMProvider(provider or config.provider)
        self.base_url = base_url or config.base_url
        self.default_model = model or config.default_model
        self.function_calling_model = config.function_calling_model
        self.code_model = config.code_model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

        # Initialize clients based on provider
        self._init_clients()

    def _init_clients(self):
        """Initialize LLM clients based on provider"""
        if self.provider == LLMProvider.OLLAMA:
            if not OLLAMA_AVAILABLE:
                raise ImportError("Ollama not available. Install with: pip install ollama")

            self.ollama_client = ollama.Client(host=self.base_url)

            # OpenAI-compatible client (for LangChain)
            self.openai_client = OpenAI(
                base_url=f"{self.base_url}/v1",
                api_key="ollama"  # Ollama doesn't require real key
            )
            self.async_openai_client = AsyncOpenAI(
                base_url=f"{self.base_url}/v1",
                api_key="ollama"
            )

        elif self.provider == LLMProvider.LM_STUDIO:
            # LM Studio uses OpenAI-compatible API on port 1234
            self.openai_client = OpenAI(
                base_url=self.base_url,
                api_key="lm-studio"
            )
            self.async_openai_client = AsyncOpenAI(
                base_url=self.base_url,
                api_key="lm-studio"
            )

        elif self.provider == LLMProvider.LLAMA_CPP:
            # Direct llama.cpp integration
            try:
                from llama_cpp import Llama
                self.llama_cpp_client = Llama(
                    model_path=self.default_model,  # Should be path to GGUF file
                    n_ctx=8192,
                    n_gpu_layers=35  # Adjust based on GPU VRAM
                )
            except ImportError:
                raise ImportError("llama-cpp-python not available. Install with: pip install llama-cpp-python")

    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate completion using the configured LLM provider

        Args:
            prompt: User prompt
            model: Override default model
            temperature: Override default temperature
            max_tokens: Override default max tokens
            system_prompt: Optional system message
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text response
        """
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens or self.max_tokens

        if self.provider == LLMProvider.OLLAMA:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.ollama_client.chat(
                model=model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    **kwargs
                }
            )
            return response['message']['content']

        elif self.provider in [LLMProvider.LM_STUDIO, LLMProvider.LLAMA_CPP]:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content

    async def acomplete(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Async version of complete()"""
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens or self.max_tokens

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.async_openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    def complete_with_functions(
        self,
        prompt: str,
        functions: List[Dict[str, Any]],
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion with function calling support

        Best models for this: qwen2.5:7b, llama3.1:8b+

        Args:
            prompt: User prompt
            functions: List of function definitions (OpenAI format)
            model: Override default (uses function_calling_model)

        Returns:
            Dict with 'content' and optionally 'function_call'
        """
        model = model or self.function_calling_model

        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            functions=functions,
            **kwargs
        )

        choice = response.choices[0]
        result = {
            "content": choice.message.content,
            "function_call": None
        }

        if hasattr(choice.message, 'function_call') and choice.message.function_call:
            result["function_call"] = {
                "name": choice.message.function_call.name,
                "arguments": choice.message.function_call.arguments
            }

        return result

    def get_langchain_llm(self, model: Optional[str] = None) -> ChatOpenAI:
        """
        Get LangChain-compatible LLM client

        Returns:
            ChatOpenAI instance configured for local provider
        """
        model = model or self.default_model

        return ChatOpenAI(
            model=model,
            base_url=f"{self.base_url}/v1" if self.provider == LLMProvider.OLLAMA else self.base_url,
            api_key="ollama" if self.provider == LLMProvider.OLLAMA else "lm-studio",
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

    def list_models(self) -> List[str]:
        """List available models from the provider"""
        if self.provider == LLMProvider.OLLAMA:
            models = self.ollama_client.list()
            return [model['name'] for model in models['models']]

        elif self.provider == LLMProvider.LM_STUDIO:
            # LM Studio model list endpoint
            try:
                response = self.openai_client.models.list()
                return [model.id for model in response.data]
            except:
                return ["Model list not available"]

        return []

    def pull_model(self, model_name: str) -> bool:
        """
        Pull/download a model (Ollama only)

        Args:
            model_name: Model to pull (e.g., "qwen2.5:7b")

        Returns:
            True if successful
        """
        if self.provider != LLMProvider.OLLAMA:
            raise NotImplementedError("Model pulling only supported for Ollama")

        try:
            self.ollama_client.pull(model_name)
            return True
        except Exception as e:
            print(f"Failed to pull model {model_name}: {e}")
            return False

    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available locally"""
        return model_name in self.list_models()


# Global LLM manager instance
_llm_manager: Optional[LLMManager] = None


def get_llm() -> LLMManager:
    """Get the global LLM manager instance"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager

import logging
from typing import Any

import yaml
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

from src.config import settings

LOGGER = logging.getLogger("llm")


class LLMAnalysisError(Exception):
    pass


class ProductAnalyzer:
    def __init__(self, api_key: str = ""):
        self.api_key = SecretStr(api_key)

        with open(settings.TEMPLATE_PATH) as f:
            templates = yaml.safe_load(f)
        self.templates: dict[str, str] = templates

        self.llm_chain = self._get_chain()

    def _get_chain(self) -> LLMChain:
        if not self.api_key:
            raise ValueError("API Key not set")

        input_variables = [
            "title",
            "category",
            "reviews_analysis",
            "average_rating",
        ]

        system_message = SystemMessage(self.templates["system-prompt"])
        human_message = HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=input_variables,
                template=self.templates["summary-prompt"],
            )
        )

        prompt = ChatPromptTemplate(
            input_variables=input_variables, messages=[system_message, human_message]
        )

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=0.7,
            api_key=self.api_key,
        )

        return LLMChain(llm=llm, prompt=prompt)

    def analyze_product(self, data: dict[str, str | float | list[str]]) -> str:
        if not self.llm_chain:
            raise ValueError("LLM Chain not set properly.")
        if isinstance(data["rating"], str):
            rating = int(data["rating"])
        else:
            rating = -1

        try:
            context = {
                "title": data["product"],
                "category": data.get("category", "No category available"),
                "reviews_analysis": self._prepare_review_analysis(data["comments"]),
                "average_rating": rating if rating > 0 else "Unknown",
            }

            LOGGER.info("Running Gemini analysis...")
            result = self.llm_chain.run(context)
            LOGGER.info("Analysis complete")
            return result
        except Exception as e:
            LOGGER.error(f"LLM Chain error: {str(e)}")
            raise LLMAnalysisError()

    def _prepare_review_analysis(self, comments_data: Any) -> str:
        if not isinstance(comments_data, list):
            raise ValueError("Incorrect data format")

        reviews_analysis: list[str] = []
        for comm in comments_data:
            context = {"comment": comm}
            review_text = self.templates["comment-template"].format(**context)
            reviews_analysis.append(review_text)

        if not reviews_analysis:
            raise LLMAnalysisError("No comments found")
        return "\n".join(reviews_analysis)

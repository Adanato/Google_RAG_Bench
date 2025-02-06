import abc
from abc import ABC, abstractmethod

def get_prompt_template(topic: str) -> str:
    """
    Generates the base prompt text for creating a single obscure question.
    """
    return f"""
Given the seed topic: "{topic}", create a single question that:

1. Is Not Well-Known:
   - The question should be obscure enough that the correct answer is unlikely to appear as the first search result.

2. Appears Conflicting or Ambiguous on the Surface:
   - There may be multiple conflicting or misleading sources online.

3. Has a Single, Correct Answer:
   - The question should have only one officially recognized or verifiable answer.

4. Requires Multi-Step or Layered Reasoning:
   - It’s not answered by a simple fact lookup; the question might reference official designations, historical records, or particular certifications that aren’t widely known.

5. Is Grammatically Natural:
   - The question should read like something a curious person would genuinely ask.

6. Is Supported by Written Articles:
   - The answer should be corroborated by at least one credible or official source, even if it doesn’t appear at the top of search results.

Output Format:
Provide the final question in a single sentence, keeping it clear and specific. ###output: <question>
""".strip()


class BaseQueryGeneration(ABC):
    """
    Abstract base class for generating a single, obscure query
    based on a seed topic and a known prompt template.
    """

    @abstractmethod
    def generate_query(self, topic: str) -> str:
        """
        Given a seed topic, return a single question that meets the
        'obscure, conflicting, single-answer' criteria.
        
        This method should utilize the underlying LLM or approach
        (e.g., Hugging Face, OpenAI) to transform the prompt template
        into a final question.
        """
        pass

class VllmQueryGeneration(BaseQueryGeneration):
    """
    Concrete implementation of BaseQueryGeneration that calls a Hugging Face model
    (e.g., text-generation pipeline) to produce the query.
    """

    def __init__(self, hf_pipeline):
        """
        :param hf_pipeline: A Hugging Face text generation pipeline
                            (e.g., transformers.pipeline("text-generation", model=...))
        """
        self.hf_pipeline = hf_pipeline

    def generate_query(self, topic: str) -> str:
        # 1. Get the prompt template
        prompt_text = get_prompt_template(topic)
        
        # 2. Call your Hugging Face pipeline
        #    Example usage depends on your pipeline configuration
        #    We'll assume you do something like:
        responses = self.hf_pipeline(prompt_text, max_length=200, do_sample=True, top_p=0.9)
        
        # 3. Extract the model-generated text
        generated_text = responses[0]['generated_text']
        
        # 4. (Optional) Post-process the output to isolate the single question
        #    This could involve splitting, trimming, or applying any required logic.
        #    For now, let's assume the model returns a direct question at the end.
        
        return generated_text.strip()




import abc
from abc import ABC, abstractmethod
from vllm import SamplingParams

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

    def __init__(self, model_name):
        self.model_name = model_name
        self.tokenizer = 
    def generate_query(self, topics: str, path) -> str:
        # Get the prompt template
        prompt_texts = [ get_prompt_template(topic) for topic in topics] 
        # I'm assuming this works for most like LLama

        instruct_prompts = [ self.tokenizer.apply_chat_template(messages)]
        
        # instantiate vllm here or cuda memory will persist
        vllm = 
        sampling_params = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=256)
        vllm.generate(instruct_prompts, sampling_params)
        
        responses = vllm.outputs
        pickle(responses)
        return 0




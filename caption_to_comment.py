import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import random
import re
from typing import List, Optional


class LinkedInCommentGenerator:
    def __init__(self, model_name: str = "microsoft/DialoGPT-small"):
        """
        Initialize the LinkedIn comment generator with a lightweight model.

        Alternative lightweight models you can try:
        - "microsoft/DialoGPT-small" (good for conversational responses)
        - "distilgpt2" (lightweight GPT-2 variant)
        - "gpt2" (original GPT-2, small version)
        - "microsoft/DialoGPT-medium" (slightly larger but better quality)
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading model: {model_name} on {self.device}")

        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Move model to device
        self.model.to(self.device)

        # Create text generation pipeline
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1,
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
            max_length=150,
            pad_token_id=self.tokenizer.eos_token_id
        )

    def create_comment_prompts(self, post_content: str) -> List[str]:
        """Create various prompt templates for generating different types of comments."""

        prompts = [
            # Perspective-adding prompts
            f"LinkedIn post: '{post_content}'\n\nThoughtful comment that adds a new perspective:",

            # Personal insight prompts
            f"LinkedIn post: '{post_content}'\n\nPersonal insight comment starting with 'I believed' or 'I used to think':",

            # Challenge prompts (respectful)
            f"LinkedIn post: '{post_content}'\n\nRespectful comment that challenges or questions a point:",

            # Amplification prompts
            f"LinkedIn post: '{post_content}'\n\nComment that amplifies the core message in a fresh way:",

            # Experience-based prompts
            f"LinkedIn post: '{post_content}'\n\nComment sharing relevant professional experience:",
        ]

        return prompts

    def generate_single_comment(self, prompt: str) -> str:
        """Generate a single comment based on the given prompt."""
        try:
            # Generate response
            outputs = self.generator(
                prompt,
                max_new_tokens=60,
                num_return_sequences=1,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1
            )

            # Extract the generated text
            generated_text = outputs[0]['generated_text']

            # Remove the original prompt from the output
            comment = generated_text.replace(prompt, "").strip()

            # Clean up the comment
            comment = self.clean_comment(comment)
            print(comment)
            return comment

        except Exception as e:
            print(f"Error generating comment: {e}")
            return self.get_fallback_comment()

    def clean_comment(self, comment: str) -> str:
        """Clean and format the generated comment."""
        # Remove extra whitespace and newlines
        comment = re.sub(r'\s+', ' ', comment).strip()

        # Remove quotes if they wrap the entire comment
        if comment.startswith('"') and comment.endswith('"'):
            comment = comment[1:-1]

        # Ensure the comment ends with proper punctuation
        if comment and comment[-1] not in '.!?':
            comment += '.'

        # Capitalize first letter
        if comment:
            comment = comment[0].upper() + comment[1:]

        return comment

    def get_fallback_comment(self) -> str:
        """Return a fallback comment if generation fails."""
        fallbacks = [
            "I used to think this was straightforward, but your perspective adds important nuance to consider.",
            "This resonates with my experience. I believed the conventional approach was best until I encountered a similar situation.",
            "I appreciate how you've framed this challenge. It makes me reconsider my initial assumptions.",
            "Your insight reminds me of a lesson I learned the hard way - sometimes the obvious solution isn't the right one.",
            "I used to approach this differently, but your point about the human element is spot-on."
        ]
        return random.choice(fallbacks)

    def generate_linkedin_comment(self, post_caption: str, num_attempts: int = 3) -> str:
        """
        Generate an engaging LinkedIn comment for the given post caption.

        Args:
            post_caption (str): The LinkedIn post content
            num_attempts (int): Number of generation attempts

        Returns:
            str: Generated LinkedIn comment
        """
        if not post_caption.strip():
            return "Please provide a valid post caption."

        print(f"Generating comment for post: '{post_caption[:100]}...'")

        # Create different prompt templates
        prompts = self.create_comment_prompts(post_caption)

        best_comment = ""
        best_score = 0

        for attempt in range(num_attempts):
            # Try different prompts
            prompt = random.choice(prompts)
            comment = self.generate_single_comment(prompt)

            # Score the comment (basic quality check)
            score = self.score_comment(comment)

            if score > best_score:
                best_score = score
                best_comment = comment

        # If no good comment was generated, use fallback
        if best_score < 3:
            best_comment = self.get_fallback_comment()

        return best_comment

    def score_comment(self, comment: str) -> int:
        """Simple scoring system for comment quality."""
        score = 0

        # Length check (not too short, not too long)
        if 20 <= len(comment) <= 200:
            score += 2

        # Check for generic phrases (penalize)
        generic_phrases = ['great post', 'well said',
                           'nice share', 'good point', 'totally agree']
        if not any(phrase in comment.lower() for phrase in generic_phrases):
            score += 2

        # Reward personal perspective starters
        perspective_starters = ['i used to', 'i believed',
                                'i thought', 'in my experience', 'i learned']
        if any(starter in comment.lower() for starter in perspective_starters):
            score += 3

        # Check for question marks (engagement)
        if '?' in comment:
            score += 1

        # Penalize very generic responses
        if len(comment.split()) < 5:
            score -= 2

        return score


def main():
    """Main function to demonstrate the LinkedIn comment generator."""

    # Initialize the generator
    print("Initializing LinkedIn Comment Generator...")
    generator = LinkedInCommentGenerator()

    # Example usage
    sample_posts = [

    ]

    print("\n" + "="*60)
    print("LINKEDIN COMMENT GENERATOR - DEMO")
    print("="*60)

    for i, post in enumerate(sample_posts, 1):
        print(f"\nExample {i}:")
        print(f"Post: {post}")
        print(
            f"Generated Comment: {generator.generate_linkedin_comment(post)}")
        print("-" * 60)

    # Interactive mode
    print("\nInteractive Mode - Enter your LinkedIn post caption:")
    while True:
        user_input = input("\nPost caption (or 'quit' to exit): ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            break

        if user_input:
            comment = generator.generate_linkedin_comment(user_input)
            print(f"\nGenerated Comment: {comment}")
        else:
            print("Please enter a valid post caption.")

    print("Thank you for using the LinkedIn Comment Generator!")


if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    except ImportError:
        print("Please install required packages:")
        print("pip install torch transformers")
        exit(1)

    main()

import unittest

from agentic_workflow import knowledge_base
from agentic_workflow.workflow import run_simple


class RetrieverWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Build a tiny index for testing purposes
        docs = [
            "दिल्ली भारत की राजधानी है।",
            "मुंबई महाराष्ट्र की राजधानी है।",
            "मैं हिंदी सीख रहा हूँ।",
        ]
        knowledge_base.build_index(docs, rebuild=True)

    def test_retrieval(self):
        result = run_simple("भारत की राजधानी", top_k=2)
        context = result.get("context", [])
        self.assertTrue(any("दिल्ली" in p for p in context))
        self.assertGreaterEqual(len(context), 1)
        
    def test_end_to_end(self):
        """Test full workflow: retrieval → prompt → LLM."""
        result = run_simple("राजधानी क्या है?", top_k=2)
        
        # Check each stage worked
        self.assertIn("context", result)
        self.assertIn("prompt", result)
        self.assertIn("response", result)
        
        # Response should be non-empty and mention Delhi
        response = result["response"]
        self.assertTrue(response and len(response) > 0)
        self.assertTrue(
            "दिल्ली" in response or "Delhi" in response,
            f"Response should mention Delhi: {response}"
        )


if __name__ == "__main__":
    unittest.main()

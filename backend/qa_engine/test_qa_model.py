# -*- coding: utf-8 -*-
from qa_model import qa_model

def test_qa_generation():
    test_transcript = """खरगोश और कछुआ याद है ना तुम्हे आज सोमवार है एक घंटे बाद ही दौड़ होनी है याद है भाई मेरी तो पूरी तैयारी है दौड़ शुरू हुई कछुआ तो बहुत पीछे है"""
    
    # Test novice questions
    print("\nTesting Novice Questions:")
    response = qa_model.generate_questions(test_transcript, "novice")
    print(response)
    
    # Test MCQ generation
    print("\nTesting MCQ Generation:")
    response = qa_model.generate_questions(test_transcript, "mcq")
    print(response)
    
    # Test fill in the blanks
    print("\nTesting Fill in the Blanks:")
    response = qa_model.generate_questions(test_transcript, "fill_blanks")
    print(response)

if __name__ == "__main__":
    test_qa_generation() 
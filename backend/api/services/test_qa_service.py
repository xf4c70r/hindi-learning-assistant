from api.services.qa_service import qa_service

def test_qa_service():
    test_transcript = """खरगोश और कछुआ याद है ना तुम्हे आज सोमवार है एक घंटे बाद ही दौड़ होनी है याद है भाई मेरी तो पूरी तैयारी है दौड़ शुरू हुई कछुआ तो बहुत पीछे है"""
    
    # Test question type validation
    print("\nTesting question type validation:")
    print("Is 'novice' valid?", qa_service.validate_question_type("novice"))
    print("Is 'invalid' valid?", qa_service.validate_question_type("invalid"))
    
    # Test getting supported types
    print("\nSupported question types:", qa_service.get_supported_question_types())
    
    # Test question generation for each type
    for q_type in qa_service.get_supported_question_types():
        print(f"\nTesting {q_type} question generation:")
        try:
            questions = qa_service.generate_questions(test_transcript, q_type)
            print(f"Successfully generated {len(questions['qa_pairs'])} questions")
            print("First question:", questions['qa_pairs'][0])
        except Exception as e:
            print(f"Error generating {q_type} questions:", str(e))

if __name__ == "__main__":
    test_qa_service() 
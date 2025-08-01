from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId

from agentic_workflow.workflow import run_simple
from agentic_workflow import knowledge_base
from .services.session_service import create_session, update_session, get_session

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_session(request, video_id):
    """Kick off a guided learning session.

    Body JSON:
      { "query": "<learner question>" }
    Returns session_id and first response.
    """
    query = request.data.get("query")
    if not query:
        return Response({"error": "query is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Run workflow to get initial answer (no user answer yet)
    state = run_simple(query)
    # expected answer is model's response
    expected_answer = state.get("response", "")

    initial_state = {
        "query": query,
        "expected_answer": expected_answer,
        "context": state.get("context", []),
    }
    session_id = create_session(str(request.user.id), video_id, initial_state)

    return Response({
        "session_id": session_id,
        "question": query,
        "answer": expected_answer
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request, session_id):
    """Learner submits an answer; run analyzer and return feedback."""
    user_answer = request.data.get("answer", "")
    session_doc = get_session(session_id)
    if not session_doc:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    state = session_doc.get("state", {})
    state["user_answer"] = user_answer

    # Run only analyzer node manually
    from agentic_workflow.performance_analyzer import analyze_performance
    new_state = analyze_performance(state)
    update_session(session_id, new_state)

    return Response({
        "is_correct": new_state.get("is_correct"),
        "score": new_state.get("score"),
    })
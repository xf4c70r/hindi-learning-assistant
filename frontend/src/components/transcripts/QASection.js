import React, { useState, useEffect, useCallback } from 'react';
import {
    Box,
    Button,
    Card,
    CardContent,
    FormControl,
    FormControlLabel,
    Radio,
    RadioGroup,
    TextField,
    Typography,
    Select,
    MenuItem,
    Alert,
    CircularProgress,
    Chip,
    Snackbar
} from '@mui/material';
import qaService from '../../services/qaService';
import './QASection.css';

const QASection = ({ transcriptId }) => {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedType, setSelectedType] = useState('novice');
    const [answers, setAnswers] = useState({});
    const [feedback, setFeedback] = useState({});
    const [score, setScore] = useState(0);
    const [showAnswers, setShowAnswers] = useState(false);
    const [submitting, setSubmitting] = useState(null);

    const questionTypes = [
        { value: 'novice', label: 'Novice Questions' },
        { value: 'mcq', label: 'Multiple Choice Questions' },
        { value: 'fill_blanks', label: 'Fill in the Blanks' }
    ];

    const loadQuestions = useCallback(async () => {
        try {
            const data = await qaService.getQuestions(transcriptId);
            setQuestions(data);
            setError(null);
        } catch (err) {
            setError(err.message || 'Failed to load questions');
        }
    }, [transcriptId]);

    useEffect(() => {
        loadQuestions();
    }, [loadQuestions]);

    const handleGenerateQuestions = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await qaService.generateQuestions(transcriptId, selectedType);
            if (response.questions && Array.isArray(response.questions)) {
                const formattedQuestions = response.questions.map(q => ({
                    id: q._id || q.id,  // Handle both MongoDB _id and Django id
                    question_text: q.question_text || q.question,
                    answer: q.answer,
                    question_type: q.question_type || q.type || selectedType,
                    options: q.options || []
                }));
                setQuestions(prevQuestions => [...prevQuestions, ...formattedQuestions]);
                setAnswers({});
                setFeedback({});
                setScore(0);
                setShowAnswers(false);
            } else {
                setError('No questions were generated');
            }
        } catch (err) {
            setError(err.message || 'Failed to generate questions');
        } finally {
            setLoading(false);
        }
    };

    const handleAnswerChange = (questionId, answer) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: answer
        }));
        // Clear feedback when answer changes
        setFeedback(prev => ({
            ...prev,
            [questionId]: null
        }));
    };

    const handleSubmitAnswer = async (questionId) => {
        setSubmitting(questionId);
        try {
            const response = await qaService.answerQuestion(
                transcriptId,
                questionId,
                answers[questionId]
            );
            
            // Handle both MongoDB and Django response formats
            const feedbackData = {
                is_correct: response.is_correct,
                feedback: response.is_correct ? 'Correct!' : 'Incorrect. Try again!',
                correct_answer: response.is_correct ? null : response.correct_answer
            };
            
            setFeedback(prev => ({
                ...prev,
                [questionId]: feedbackData
            }));
            
            // Update score if answer is correct
            if (feedbackData.is_correct) {
                setScore(prev => prev + 1);
            }
        } catch (err) {
            setError(err.message || 'Failed to submit answer');
        } finally {
            setSubmitting(null);
        }
    };

    const renderQuestionInput = (question) => {
        switch (question.question_type || question.type) {  // Handle both formats
            case 'mcq':
                return (
                    <RadioGroup
                        value={answers[question.id] || ''}
                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                    >
                        {question.options?.map((option, index) => (
                            <FormControlLabel
                                key={index}
                                value={option}
                                control={<Radio />}
                                label={option}
                                disabled={!!feedback[question.id]}
                            />
                        ))}
                    </RadioGroup>
                );
            case 'fill_blanks':
                // Split the question text by the blank marker
                const parts = question.question_text.split('____');
                return (
                    <Box>
                        <Typography variant="body1" sx={{ mb: 1 }}>
                            {parts[0]}
                            <TextField
                                sx={{ mx: 1, width: '150px' }}
                                size="small"
                                value={answers[question.id] || ''}
                                onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                placeholder="भरें"
                                variant="outlined"
                                disabled={!!feedback[question.id]}
                            />
                            {parts[1]}
                        </Typography>
                    </Box>
                );
            default:
                return (
                    <TextField
                        fullWidth
                        multiline
                        rows={3}
                        value={answers[question.id] || ''}
                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                        placeholder="Enter your answer"
                        variant="outlined"
                        disabled={!!feedback[question.id]}
                    />
                );
        }
    };

    return (
        <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                <FormControl sx={{ minWidth: 200 }}>
                    <Select
                        value={selectedType}
                        onChange={(e) => setSelectedType(e.target.value)}
                        displayEmpty
                    >
                        {questionTypes.map(type => (
                            <MenuItem key={type.value} value={type.value}>
                                {type.label}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <Button
                    variant="contained"
                    onClick={handleGenerateQuestions}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : null}
                >
                    {loading ? 'Generating...' : 'Generate Questions'}
                </Button>
                {questions.length > 0 && (
                    <Button
                        variant="outlined"
                        onClick={() => setShowAnswers(!showAnswers)}
                    >
                        {showAnswers ? 'Hide Answers' : 'Show Answers'}
                    </Button>
                )}
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {questions.length > 0 && (
                <Typography variant="h6" sx={{ mb: 2 }}>
                    Score: {score}/{questions.length}
                </Typography>
            )}

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {questions.map((question, index) => (
                    <Card key={question.id} variant="outlined">
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                <Typography variant="subtitle1">
                                    Question {index + 1}
                                </Typography>
                                <Chip
                                    label={(question.question_type || question.type || selectedType).toUpperCase()}
                                    color="primary"
                                    size="small"
                                />
                            </Box>
                            
                            <Typography variant="body1" sx={{ mb: 2 }}>
                                {question.question_text}
                            </Typography>

                            {!showAnswers && !feedback[question.id] && (
                                <>
                                    {renderQuestionInput(question)}
                                    <Box sx={{ mt: 2 }}>
                                        <Button
                                            variant="contained"
                                            onClick={() => handleSubmitAnswer(question.id)}
                                            disabled={!answers[question.id] || submitting === question.id}
                                            startIcon={submitting === question.id ? <CircularProgress size={20} /> : null}
                                        >
                                            {submitting === question.id ? 'Submitting...' : 'Submit Answer'}
                                        </Button>
                                    </Box>
                                </>
                            )}

                            {feedback[question.id] && (
                                <Alert
                                    severity={feedback[question.id].is_correct ? 'success' : 'error'}
                                    sx={{ mt: 2 }}
                                >
                                    {feedback[question.id].feedback}
                                    {!feedback[question.id].is_correct && (
                                        <Typography sx={{ mt: 1 }}>
                                            Correct answer: {feedback[question.id].correct_answer}
                                        </Typography>
                                    )}
                                </Alert>
                            )}

                            {showAnswers && (
                                <Box sx={{ mt: 2 }}>
                                    <Typography variant="subtitle2" color="primary">
                                        Correct Answer:
                                    </Typography>
                                    <Typography variant="body1">
                                        {question.answer}
                                    </Typography>
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                ))}
            </Box>

            {questions.length === 0 && !loading && (
                <Typography variant="body1" color="text.secondary" align="center">
                    No questions generated yet. Click the button above to generate questions.
                </Typography>
            )}

            <Snackbar
                open={!!error}
                autoHideDuration={6000}
                onClose={() => setError(null)}
                message={error}
            />
        </Box>
    );
};

export default QASection; 
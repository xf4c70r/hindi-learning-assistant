import React, { useState } from 'react';
import {
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    RadioGroup,
    FormControlLabel,
    Radio,
    Box,
    Alert,
    CircularProgress
} from '@mui/material';
import practiceService from '../../services/practiceService';

const QuestionCard = ({ question, onAnswerSubmit }) => {
    const [answer, setAnswer] = useState('');
    const [feedback, setFeedback] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        if (!answer.trim()) return;
        
        setLoading(true);
        try {
            const response = await practiceService.submitAnswer(question._id, {
                answer,
                video_id: question.video_id,
                type: question.type,
                is_correct: answer.toLowerCase() === question.answer.toLowerCase()
            });
            
            setFeedback({
                type: response.success ? 'success' : 'error',
                message: response.success ? 'Correct!' : 'Incorrect. Try again!'
            });
            
            if (onAnswerSubmit) {
                onAnswerSubmit(response);
            }
        } catch (error) {
            setFeedback({
                type: 'error',
                message: error.message || 'Failed to submit answer'
            });
        } finally {
            setLoading(false);
        }
    };

    const renderAnswerInput = () => {
        switch (question.type) {
            case 'mcq':
                return (
                    <RadioGroup
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                    >
                        {question.options?.map((option, index) => (
                            <FormControlLabel
                                key={index}
                                value={option}
                                control={<Radio />}
                                label={option}
                                disabled={loading}
                            />
                        ))}
                    </RadioGroup>
                );
            
            case 'fill_blanks':
                const parts = question.question_text.split('____');
                return (
                    <Box>
                        <Typography variant="body1" sx={{ mb: 1 }}>
                            {parts[0]}
                            <TextField
                                sx={{ mx: 1, width: '150px' }}
                                size="small"
                                value={answer}
                                onChange={(e) => setAnswer(e.target.value)}
                                placeholder="भरें"
                                variant="outlined"
                                disabled={loading}
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
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                        placeholder="Enter your answer"
                        variant="outlined"
                        disabled={loading}
                    />
                );
        }
    };

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    {question.type === 'fill_blanks' ? 
                        'Fill in the blank:' : 
                        question.question_text
                    }
                </Typography>

                <Box sx={{ my: 2 }}>
                    {renderAnswerInput()}
                </Box>

                {feedback && (
                    <Alert 
                        severity={feedback.type} 
                        sx={{ mb: 2 }}
                        onClose={() => setFeedback(null)}
                    >
                        {feedback.message}
                    </Alert>
                )}

                <Button
                    variant="contained"
                    onClick={handleSubmit}
                    disabled={!answer.trim() || loading}
                    fullWidth
                >
                    {loading ? <CircularProgress size={24} /> : 'Submit Answer'}
                </Button>
            </CardContent>
        </Card>
    );
};

export default QuestionCard; 
import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import { queryWord } from '../../services/vocabularyService';

const WordQuery = () => {
  const [word, setWord] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleQuery = async () => {
    if (!word.trim()) {
      setError('Please enter a word');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await queryWord(word);
      setResult(response);  // Store the entire response
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to query word');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleQuery();
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          value={word}
          onChange={(e) => setWord(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter a Hindi word"
          variant="outlined"
          size="medium"
          fullWidth
          disabled={loading}
        />
        <Button
          variant="contained"
          onClick={handleQuery}
          disabled={loading}
          sx={{ minWidth: 100 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Query'}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      {result && (
        <Card>
          <CardContent>
            <Typography variant="h6">{result.word}</Typography>
            {result.data && (
              <>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Meaning: {result.data.meaning}
            </Typography>
                {result.data.example && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1">Example:</Typography>
              <Typography variant="body2" color="text.secondary">
                      Hindi: {result.data.example.hindi}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                      English: {result.data.example.english}
              </Typography>
            </Box>
                )}
                {result.frequency && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Search frequency: {result.frequency}
                  </Typography>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default WordQuery;

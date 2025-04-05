import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  Paper
} from '@mui/material';
import TranscriptCard from '../components/TranscriptCard';
import transcriptService from '../services/transcriptService';

const TranscriptsPage = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [transcripts, setTranscripts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchTranscripts();
  }, []);

  const fetchTranscripts = async () => {
    try {
      const data = await transcriptService.getAllTranscripts();
      setTranscripts(data);
    } catch (error) {
      setError('Failed to fetch transcripts. Please try again later.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Extract video ID from URL
      const videoId = videoUrl.split('v=')[1]?.split('&')[0];
      if (!videoId) {
        throw new Error('Invalid YouTube URL');
      }

      const newTranscript = await transcriptService.createTranscript(videoId);
      setTranscripts([newTranscript, ...transcripts]);
      setVideoUrl('');
      setSuccess('Transcript created successfully!');
    } catch (error) {
      setError(error.message || 'Failed to create transcript. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await transcriptService.deleteTranscript(id);
      setTranscripts(transcripts.filter(t => t.id !== id));
      setSuccess('Transcript deleted successfully!');
    } catch (error) {
      setError('Failed to delete transcript. Please try again.');
    }
  };

  const handleUpdate = (updatedTranscript) => {
    setTranscripts(transcripts.map(t => 
      t.id === updatedTranscript.id ? updatedTranscript : t
    ));
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        My Transcripts
      </Typography>

      <Paper 
        component="form" 
        onSubmit={handleSubmit}
        sx={{ p: 3, mb: 4, backgroundColor: 'background.paper' }}
      >
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            label="YouTube Video URL"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            disabled={loading}
          />
          <Button 
            variant="contained" 
            type="submit"
            disabled={loading || !videoUrl}
            sx={{ minWidth: 200 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Create Transcript'}
          </Button>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Box sx={{ mt: 4 }}>
        {transcripts.length === 0 ? (
          <Typography variant="body1" color="text.secondary" align="center">
            No transcripts yet. Create one by pasting a YouTube URL above!
          </Typography>
        ) : (
          transcripts.map(transcript => (
            <TranscriptCard
              key={transcript.id}
              transcript={transcript}
              onDelete={handleDelete}
              onUpdate={handleUpdate}
            />
          ))
        )}
      </Box>
    </Container>
  );
};

export default TranscriptsPage; 
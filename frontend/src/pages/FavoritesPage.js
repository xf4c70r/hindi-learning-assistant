import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import TranscriptCard from '../components/TranscriptCard';
import transcriptService from '../services/transcriptService';

const FavoritesPage = () => {
  const [transcripts, setTranscripts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchFavoriteTranscripts();
  }, []);

  const fetchFavoriteTranscripts = async () => {
    try {
      setLoading(true);
      const data = await transcriptService.getFavoriteTranscripts();
      setTranscripts(data);
      setLoading(false);
    } catch (error) {
      setError('Failed to fetch favorite transcripts. Please try again later.');
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await transcriptService.deleteTranscript(id);
      setTranscripts(transcripts.filter(t => t.id !== id));
      setSuccess('Transcript removed successfully!');
    } catch (error) {
      setError('Failed to delete transcript. Please try again.');
    }
  };

  const handleUpdate = (updatedTranscript) => {
    // If transcript is unfavorited, remove it from the favorites list
    if (!updatedTranscript.is_favorite) {
      setTranscripts(transcripts.filter(t => t.id !== updatedTranscript.id));
    } else {
      // Update the transcript in the list
      setTranscripts(transcripts.map(t => 
        t.id === updatedTranscript.id ? updatedTranscript : t
      ));
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        My Favorite Transcripts
      </Typography>

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

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box sx={{ mt: 4 }}>
          {transcripts.length === 0 ? (
            <Typography variant="body1" color="text.secondary" align="center">
              No favorite transcripts yet. Heart a transcript on the Transcripts page to add it here!
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
      )}
    </Container>
  );
};

export default FavoritesPage; 
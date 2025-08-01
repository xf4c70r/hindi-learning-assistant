import React, { useState, useEffect, useCallback } from 'react';
import { queryWord, getUserWords, toggleWordFavorite, updateWordNotes } from '../services/vocabularyService';
import { 
  Box, 
  TextField, 
  Button, 
  Card, 
  CardContent, 
  Typography, 
  IconButton, 
  Grid, 
  CircularProgress,
  Paper,
  Divider,
  Container,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { Favorite, FavoriteBorder, Search, TranslateOutlined, Edit } from '@mui/icons-material';

const VocabularyManager = () => {
  const [searchWord, setSearchWord] = useState('');
  const [userWords, setUserWords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const [editingWord, setEditingWord] = useState(null);
  const [editingNotes, setEditingNotes] = useState('');

  const loadUserWords = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getUserWords(showFavoritesOnly);
      setUserWords(response.words || []);
      setError('');
    } catch (err) {
      setError('Failed to load words. Please try again.');
      console.error('Error loading words:', err);
    } finally {
      setLoading(false);
    }
  }, [showFavoritesOnly]);

  useEffect(() => {
    loadUserWords();
  }, [loadUserWords]);

  const handleWordSearch = async () => {
    if (!searchWord.trim()) {
      setError('Please enter a word to search');
      return;
    }

    try {
      setLoading(true);
      await queryWord(searchWord.trim());
      await loadUserWords();
      setSearchWord('');
      setError('');
    } catch (err) {
      setError('Failed to query word. Please try again.');
      console.error('Error querying word:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (wordId) => {
    try {
      await toggleWordFavorite(wordId);
      await loadUserWords();
    } catch (err) {
      setError('Failed to update favorite status');
      console.error('Error toggling favorite:', err);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleWordSearch();
    }
  };

  const handleEditNotes = (word) => {
    setEditingWord(word);
    setEditingNotes(word.notes || '');
  };

  const handleSaveNotes = async () => {
    try {
      await updateWordNotes(editingWord.word_id, editingNotes);
      await loadUserWords();
      setEditingWord(null);
      setEditingNotes('');
    } catch (err) {
      setError('Failed to update notes');
      console.error('Error updating notes:', err);
    }
  };

  // Helper function to format meaning data
  const formatMeaning = (meaningData) => {
    if (!meaningData) return '';
    if (typeof meaningData === 'string') return meaningData;
    if (typeof meaningData === 'object') {
      const parts = [];
      if (meaningData.meaning) parts.push(meaningData.meaning);
      if (meaningData.example) {
        if (meaningData.example.hindi && meaningData.example.english) {
          parts.push(`Example:`);
          parts.push(`${meaningData.example.hindi}`);
          parts.push(`${meaningData.example.english}`);
        }
      }
      return parts.join('\n');
    }
    return JSON.stringify(meaningData);
  };

  return (
    <Container maxWidth="lg">
      {/* Search Section */}
      <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="h6" color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TranslateOutlined /> Word Lookup
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              value={searchWord}
              onChange={(e) => setSearchWord(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter a Hindi word"
              disabled={loading}
              size="medium"
              sx={{ 
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2
                }
              }}
            />
            <Button
              variant="contained"
              onClick={handleWordSearch}
              disabled={loading}
              startIcon={<Search />}
              sx={{ px: 4, borderRadius: 2 }}
            >
              Search
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Filter and Results Section */}
      <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" color="primary">
            {showFavoritesOnly ? 'Favorite Words' : 'All Words'}
          </Typography>
          <Button
            variant={showFavoritesOnly ? "contained" : "outlined"}
            onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
            startIcon={showFavoritesOnly ? <Favorite /> : <FavoriteBorder />}
            sx={{ borderRadius: 2 }}
          >
            {showFavoritesOnly ? 'Show All' : 'Show Favorites'}
          </Button>
        </Box>

        {error && (
          <Typography color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {userWords.map((word) => (
              <Grid item xs={12} sm={6} md={4} key={word._id}>
                <Card sx={{ 
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 2,
                  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 16px rgba(0,0,0,0.1)'
                  }
                }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="h6" component="h3" sx={{ fontWeight: 500 }}>
                        {word.word}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <IconButton
                          onClick={() => handleEditNotes(word)}
                          color="primary"
                          size="small"
                          sx={{ 
                            '&:hover': { 
                              backgroundColor: 'rgba(25,118,210,0.04)'
                            } 
                          }}
                        >
                          <Edit />
                        </IconButton>
                        <IconButton
                          onClick={() => handleToggleFavorite(word.word_id)}
                          color={word.is_favorite ? "error" : "default"}
                          size="small"
                          sx={{ 
                            '&:hover': { 
                              backgroundColor: word.is_favorite ? 'rgba(244,67,54,0.04)' : 'rgba(0,0,0,0.04)'
                            } 
                          }}
                        >
                          {word.is_favorite ? <Favorite /> : <FavoriteBorder />}
                        </IconButton>
                      </Box>
                    </Box>
                    <Divider sx={{ my: 1 }} />
                    <Typography 
                      variant="body1" 
                      color="text.secondary" 
                      sx={{ 
                        mt: 1,
                        whiteSpace: 'pre-line' // This will preserve line breaks
                      }}
                    >
                      {formatMeaning(word.meaning)}
                    </Typography>
                    {word.notes && (
                      <Typography 
                        variant="body2" 
                        color="text.secondary" 
                        sx={{ 
                          mt: 2, 
                          fontStyle: 'italic',
                          whiteSpace: 'pre-line'
                        }}
                      >
                        Notes: {word.notes}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>

      {/* Notes Edit Dialog */}
      <Dialog 
        open={Boolean(editingWord)} 
        onClose={() => setEditingWord(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Edit Notes for "{editingWord?.word}"
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Notes"
            fullWidth
            multiline
            rows={4}
            value={editingNotes}
            onChange={(e) => setEditingNotes(e.target.value)}
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingWord(null)}>Cancel</Button>
          <Button onClick={handleSaveNotes} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default VocabularyManager; 
import React from 'react';
import { Container, Typography } from '@mui/material';
import VocabularyManager from '../components/VocabularyManager';

const VocabularyPage = () => {
  return (
    <Container maxWidth="lg">
      <Typography variant="h3" component="h1" gutterBottom sx={{ mt: 4 }}>
        Hindi Vocabulary
        </Typography>
      <VocabularyManager />
    </Container>
  );
};

export default VocabularyPage;

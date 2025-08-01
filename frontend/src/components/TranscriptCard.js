import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  IconButton,
  Collapse,
  Box,
  Chip,
  Tooltip,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  Alert
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Delete as DeleteIcon,
  YouTube as YouTubeIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Translate as TranslateIcon,
  QuestionAnswer as QuestionAnswerIcon,
  Book as BookIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import moment from 'moment';
import transcriptService from '../services/transcriptService';
import QASection from './transcripts/QASection';

// Styled expand button that rotates when clicked
const ExpandButton = styled((props) => {
  const { expand, ...other } = props;
  return <IconButton {...other} />;
})(({ theme, expand }) => ({
  transform: !expand ? 'rotate(0deg)' : 'rotate(180deg)',
  marginLeft: 'auto',
  transition: theme.transitions.create('transform', {
    duration: theme.transitions.duration.shortest,
  }),
}));

// Function to extract title from content
const extractTitle = (content, existingTitle) => {
  if (existingTitle && existingTitle !== "Untitled") return existingTitle;
  if (!content) return "Untitled";
  
  // Take first 5 words or up to first punctuation mark
  const firstLine = content.split(/[।?!.\n]/)[0];
  const words = firstLine.split(' ').slice(0, 5).join(' ');
  return words + '...';
};

const TranscriptCard = ({ transcript, onDelete, onUpdate }) => {
  const [expanded, setExpanded] = useState(false);
  const [qaExpanded, setQaExpanded] = useState(false);
  const [isFavorite, setIsFavorite] = useState(transcript.is_favorite);
  const [isLoading, setIsLoading] = useState(false);
  const [showTranslation, setShowTranslation] = useState(false);
  const [showVocabulary, setShowVocabulary] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [showGlossary, setShowGlossary] = useState(false);
  const [error, setError] = useState(null);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handleQAExpandClick = () => {
    setQaExpanded(!qaExpanded);
  };

  const handleTranslationClick = () => {
    setShowTranslation(!showTranslation);
  };

  const handleTranslateClick = async () => {
    if (!transcript.content) return;
    
    try {
      setIsTranslating(true);
      const response = await transcriptService.translateTranscript(transcript.id);
      const updatedTranscript = {
        ...transcript,
        translation: response.translation
      };
      if (onUpdate) {
        onUpdate(updatedTranscript);
      }
      setShowTranslation(true);
    } catch (error) {
      console.error('Failed to translate:', error);
    } finally {
      setIsTranslating(false);
    }
  };

  const handleVocabularyClick = () => {
    setShowVocabulary(!showVocabulary);
  };

  const handleFavoriteClick = async () => {
    try {
      setIsLoading(true);
      const response = await transcriptService.toggleFavorite(transcript.id);
      const updatedTranscript = {
        ...transcript,
        is_favorite: response.is_favorite
      };
      setIsFavorite(response.is_favorite);
      if (onUpdate) {
        onUpdate(updatedTranscript);
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateGlossary = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await transcriptService.generateGlossary(transcript.id);
      const updatedTranscript = {
        ...transcript,
        glossary: response.glossary
      };
      if (onUpdate) {
        onUpdate(updatedTranscript);
      }
      setShowGlossary(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const title = extractTitle(transcript.content, transcript.title);
  const createdDate = moment(transcript.created_at).format('MMMM D, YYYY');

  // Debug log for glossary
  console.log('Glossary:', transcript.glossary);

  return (
    <Card sx={{ 
      mb: 2, 
      boxShadow: 3,
      '&:hover': {
        boxShadow: 6,
        transform: 'translateY(-2px)',
        transition: 'all 0.3s ease-in-out'
      }
    }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
          <Box>
            <Chip
              icon={<TranslateIcon />}
              label={transcript.language === 'hi' ? 'Hindi' : transcript.language}
              size="small"
              color="primary"
              sx={{ mr: 1 }}
            />
            <Tooltip title="Open in YouTube">
              <IconButton 
                size="small"
                href={`https://youtube.com/watch?v=${transcript.video_id}`}
                target="_blank"
              >
                <YouTubeIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          Created on {createdDate}
        </Typography>

        {error && <Alert message={error} type="error" showIcon />}

        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Typography paragraph sx={{ 
            mt: 2,
            backgroundColor: 'background.paper',
            p: 2,
            borderRadius: 1,
            fontFamily: 'inherit',
            lineHeight: 1.8
          }}>
            {transcript.content}
          </Typography>
          
          {transcript.translation && (
            <Collapse in={showTranslation} timeout="auto" unmountOnExit>
              <Typography 
                paragraph 
                sx={{ 
                  mt: 2,
                  backgroundColor: 'background.paper',
                  p: 2,
                  borderRadius: 1,
                  fontFamily: 'inherit',
                  lineHeight: 1.8,
                  borderTop: '1px solid rgba(0, 0, 0, 0.12)'
                }}
              >
                {transcript.translation}
              </Typography>
            </Collapse>
          )}

          {transcript.vocabulary && transcript.vocabulary.length > 0 && (
            <Collapse in={showVocabulary} timeout="auto" unmountOnExit>
              <Box
                sx={{
                  mt: 2,
                  backgroundColor: 'background.paper',
                  p: 2,
                  borderRadius: 1,
                  borderTop: '1px solid rgba(0, 0, 0, 0.12)'
                }}
              >
                <Typography variant="h6" gutterBottom>
                  Vocabulary
                </Typography>
                <List>
                  {transcript.vocabulary.map((word, index) => (
                    <ListItem key={index} sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle1" component="span" fontWeight="bold">
                              {word.word}
                            </Typography>
                            <Typography variant="body1" component="span" color="text.secondary">
                              - {word.meaning}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Box mt={1}>
                            <Typography variant="body2" component="div" color="text.secondary">
                              Example:
                            </Typography>
                            <Typography variant="body2" component="div" sx={{ mt: 0.5 }}>
                              {word.example.hindi}
                            </Typography>
                            <Typography variant="body2" component="div" color="text.secondary" sx={{ mt: 0.5 }}>
                              {word.example.english}
                            </Typography>
                          </Box>
                        }
                      />
                      {index < transcript.vocabulary.length - 1 && <Divider sx={{ my: 2, width: '100%' }} />}
                    </ListItem>
                  ))}
                </List>
              </Box>
            </Collapse>
          )}
        </Collapse>
      </CardContent>

      <Divider />

      <CardActions disableSpacing>
        <IconButton 
          aria-label="add to favorites"
          onClick={handleFavoriteClick}
          disabled={isLoading}
        >
          {isFavorite ? <FavoriteIcon color="error" /> : <FavoriteBorderIcon />}
        </IconButton>
        
        <Button
          size="small"
          onClick={() => onDelete(transcript.id)}
          startIcon={<DeleteIcon />}
          color="error"
        >
          Delete
        </Button>

        <Button
          size="small"
          onClick={handleQAExpandClick}
          startIcon={<QuestionAnswerIcon />}
          color="primary"
        >
          {qaExpanded ? 'Hide Q&A' : 'Show Q&A'}
        </Button>

        {expanded && (
          <Button
            size="small"
            onClick={handleTranslateClick}
            startIcon={<TranslateIcon />}
            color="primary"
            disabled={isTranslating}
          >
            {isTranslating ? 'Translating...' : 'Translate'}
          </Button>
        )}

        {expanded && transcript.translation && (
          <Button
            size="small"
            onClick={handleTranslationClick}
            startIcon={<TranslateIcon />}
            color="primary"
          >
            {showTranslation ? 'Hide Translation' : 'Show Translation'}
          </Button>
        )}

        {expanded && transcript.vocabulary && transcript.vocabulary.length > 0 && (
          <Button
            size="small"
            onClick={handleVocabularyClick}
            startIcon={<BookIcon />}
            color="primary"
          >
            {showVocabulary ? 'Hide Vocabulary' : 'Show Vocabulary'}
          </Button>
        )}

        {expanded && transcript.glossary && transcript.glossary.length > 0 && (
          <Button
            size="small"
            onClick={() => setShowGlossary(!showGlossary)}
            startIcon={<BookIcon />}
            color="primary"
          >
            {showGlossary ? 'Hide Glossary' : 'Show Glossary'}
          </Button>
        )}
        {expanded && (!transcript.glossary || transcript.glossary.length === 0) && (
          <Button
            size="small"
            onClick={handleGenerateGlossary}
            startIcon={<BookIcon />}
            color="primary"
            disabled={isLoading}
          >
            {isLoading ? 'Generating...' : 'Generate Glossary'}
          </Button>
        )}

        <ExpandButton
          expand={expanded}
          onClick={handleExpandClick}
          aria-expanded={expanded}
          aria-label="show more"
        >
          <ExpandMoreIcon />
        </ExpandButton>
      </CardActions>

      <Collapse in={qaExpanded} timeout="auto" unmountOnExit>
        <CardContent>
          <QASection transcriptId={transcript.id} />
        </CardContent>
      </Collapse>

      {showGlossary && transcript.glossary && (
        <div style={{ background: '#f9f9f9', padding: 16, marginTop: 16 }}>
          <Typography variant="h6" gutterBottom>
            Glossary
          </Typography>
          {transcript.glossary.map((entry) => (
            <Box key={entry.word} sx={{ mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                {entry.word}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Meaning:</strong> {entry.meaning}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Example:</strong> {entry.example}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Translation:</strong> {entry.example_translation}
              </Typography>
            </Box>
          ))}
        </div>
      )}
    </Card>
  );
};

export default TranscriptCard; 
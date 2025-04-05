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
  Divider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Delete as DeleteIcon,
  YouTube as YouTubeIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Translate as TranslateIcon,
  QuestionAnswer as QuestionAnswerIcon
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

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handleQAExpandClick = () => {
    setQaExpanded(!qaExpanded);
  };

  const handleFavoriteClick = async () => {
    try {
      setIsLoading(true);
      const updatedTranscript = await transcriptService.toggleFavorite(transcript.id);
      setIsFavorite(updatedTranscript.is_favorite);
      if (onUpdate) {
        onUpdate(updatedTranscript);
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const title = extractTitle(transcript.content, transcript.title);
  const createdDate = moment(transcript.created_at).format('MMMM D, YYYY');

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
    </Card>
  );
};

export default TranscriptCard; 
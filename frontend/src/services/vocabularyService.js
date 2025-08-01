import axios from './axiosConfig';

/**
 * Query a Hindi word for its meaning and details
 * @param {string} word - The Hindi word to query
 * @returns {Promise} Promise object with word data
 */
export const queryWord = async (word) => {
  try {
    const response = await axios.post('/vocabulary/query/', { word });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get user's saved words
 * @param {boolean} favoritesOnly - Whether to fetch only favorite words
 * @returns {Promise} Promise object with user's words
 */
export const getUserWords = async (favoritesOnly = false) => {
  try {
    const response = await axios.get(`/vocabulary/words/?favorites=${favoritesOnly}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Toggle favorite status of a word
 * @param {string} wordId - ID of the word to toggle
 * @returns {Promise} Promise object with updated favorite status
 */
export const toggleWordFavorite = async (wordId) => {
  try {
    const response = await axios.post(`/words/${wordId}/toggle_favorite/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Update notes for a word
 * @param {string} wordId - ID of the word to update
 * @param {string} notes - New notes for the word
 * @returns {Promise} Promise object with updated notes
 */
export const updateWordNotes = async (wordId, notes) => {
  try {
    const response = await axios.post(`/words/${wordId}/update_notes/`, { notes });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get trending words
 * @returns {Promise} Promise object with trending words data
 */
export const getTrendingWords = async () => {
  try {
    const response = await axios.get('/trending-words/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

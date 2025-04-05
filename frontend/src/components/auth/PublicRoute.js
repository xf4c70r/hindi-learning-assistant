import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (user) {
    // Redirect authenticated users to transcripts page
    return <Navigate to="/transcripts" replace />;
  }

  return children;
};

export default PublicRoute; 
import React from 'react';
import { Container, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import Navbar from './Navbar';

const MainContent = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  minHeight: 'calc(100vh - 64px)', // Subtract navbar height
}));

const Footer = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'light' ? '#f5f5f5' : '#121212',
  padding: theme.spacing(2),
  textAlign: 'center',
  color: theme.palette.text.secondary,
}));

const Layout = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <MainContent>
        <Container maxWidth="lg">
          {children}
        </Container>
      </MainContent>
      <Footer>
        <Container maxWidth="sm">
          © {new Date().getFullYear()} Hindi QA. All rights reserved.
        </Container>
      </Footer>
    </Box>
  );
};

export default Layout; 
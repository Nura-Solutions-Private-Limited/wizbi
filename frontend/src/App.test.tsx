import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';
import { BrowserRouter } from 'react-router-dom';

test('renders welcome message', () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
  const welcomeElement = screen.getByText(/Welcome to Wizbi/i);
  expect(welcomeElement).toBeInTheDocument();
});
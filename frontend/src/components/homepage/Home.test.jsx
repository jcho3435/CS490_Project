import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import Home from './Home'; // Adjust the import path according to your file structure

// Utility function to render the component within the context of BrowserRouter
const renderWithRouter = (ui, { route = '/' } = {}) => {
  window.history.pushState({}, 'Test page', route);
  return render(ui, { wrapper: BrowserRouter });
};

describe('Home component', () => {
  test('redirects to /translate page when the "Try it out !!!" button is clicked', () => {
    renderWithRouter(<Home />);
    // Find the button by its role and text
    const button = screen.getByRole('button', { name: /try it out !!!/i });
    fireEvent.click(button);

    // Expect the current URL to change to /translate
    expect(window.location.pathname).toBe('/translate');
  });
});

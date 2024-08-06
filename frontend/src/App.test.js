import { render, screen } from '@testing-library/react';
import App from './App';
import { BrowserRouter as Router } from 'react-router-dom';

test('renders the introductory text', () => {
  render(
    <Router>
      <App />
    </Router>
  );
  const introElement = screen.getByText(/codeCraft is where all your code translating needs are met!/i);
  expect(introElement).toBeInTheDocument();
});

//comment to push
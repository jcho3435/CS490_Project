import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom'; // Necessary for React Router context
import ReleaseNotes from './ReleaseNotes';

describe('ReleaseNotes Component', () => {
  test('renders release notes title', () => {
    render(
      <MemoryRouter>
        <ReleaseNotes />
      </MemoryRouter>
    );
    expect(screen.getByText(/codecraft v1.0/i)).toBeInTheDocument(); // Main title
  });

  test('displays tech stack section', () => {
    render(
      <MemoryRouter>
        <ReleaseNotes />
      </MemoryRouter>
    );
    const techStackHeaders = screen.getAllByText(/Tech Stack/i); // Get all elements with "Tech Stack"

    // Ensure that one of the found elements is the section title
    expect(techStackHeaders.some((el) => el.tagName === 'H2')).toBeTruthy();

    // Verify React and Flask are mentioned
    expect(screen.getByText(/Frontend-React/i)).toBeInTheDocument();
    expect(screen.getByText(/Backend-Flask/i)).toBeInTheDocument();
  });

  

  test('checks if images are displayed', () => {
    render(
      <MemoryRouter>
        <ReleaseNotes />
      </MemoryRouter>
    );
    const images = screen.getAllByRole('img'); // Check if images are displayed
    expect(images.length).toBeGreaterThan(0); // Ensure there's at least one image
  });

  
});

import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Loadtesting from './Loadtesting';

describe('Loadtesting Component', () => {
  test('renders load testing title', () => {
    render(
      <MemoryRouter>
        <Loadtesting />
      </MemoryRouter>
    );
    const title = screen.getAllByText(/Load testing/i); // Check for multiple elements with "Load testing"
    expect(title.length).toBeGreaterThan(0); // There should be at least one element with this text
  });

  test('displays section titles', () => {
    render(
      <MemoryRouter>
        <Loadtesting />
      </MemoryRouter>
    );
    expect(screen.getByText(/Testing the Requests/i)).toBeInTheDocument(); // Section title
  });

  test('checks command examples', () => {
    render(
      <MemoryRouter>
        <Loadtesting />
      </MemoryRouter>
    );
    expect(screen.getByText(/\$ ab -n 1000 -c 100/i)).toBeInTheDocument(); // Check command
    expect(screen.getByText(/\$ siege -c 255 -t 60s/i)).toBeInTheDocument(); // Check command
  });

  test('checks if images are displayed', () => {
    render(
      <MemoryRouter>
        <Loadtesting />
      </MemoryRouter>
    );
    const images = screen.getAllByRole('img'); // Find all images
    expect(images.length).toBeGreaterThan(0); // Ensure at least one image is displayed
  });
});

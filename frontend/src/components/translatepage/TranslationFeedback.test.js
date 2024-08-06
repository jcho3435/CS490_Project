import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import { BrowserRouter } from 'react-router-dom'; // Import BrowserRouter
import TranslationFeedback from './TranslationFeedback'; // Ensure correct path

jest.mock('axios');

// Mock localStorage
const mockLocalStorage = (() => {
    let store = {};
    return {
        getItem: key => store[key] || null,
        setItem: (key, value) => {
            store[key] = value.toString();
        },
        clear: () => {
            store = {};
        }
    };
})();

beforeEach(() => {
    Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true
    });
    mockLocalStorage.setItem("sessionToken", "12345");
    window.alert = jest.fn(); // Mock window.alert
});

afterEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.clear();
});

describe('TranslationFeedback component', () => {
    test('renders correctly', () => {
        render(
          <BrowserRouter>
            <TranslationFeedback />
          </BrowserRouter>
        );
        expect(screen.getByText(/Rate Translation:/i)).toBeInTheDocument();
    });

    test('clicking star updates rating', () => {
        render(
          <BrowserRouter>
            <TranslationFeedback />
          </BrowserRouter>
        );
        const firstStar = screen.getAllByText('☆')[0];
        fireEvent.click(firstStar);
        expect(screen.getAllByText('★').length).toBe(1);
    });

    test('handles textarea input', () => {
        render(
          <BrowserRouter>
            <TranslationFeedback />
          </BrowserRouter>
        );
        const textarea = screen.getByPlaceholderText(/Type here/i);
        fireEvent.change(textarea, { target: { value: 'Great job!' } });
        expect(textarea).toHaveValue('Great job!');
    });

    test('submits form and sends post request', async () => {
        axios.post.mockResolvedValue({ data: { success: true } });
        render(
          <BrowserRouter>
            <TranslationFeedback />
          </BrowserRouter>
        );

        const firstStar = screen.getAllByText('☆')[0];
        fireEvent.click(firstStar);
        const submitButton = screen.getByText(/Submit/i);
        fireEvent.click(submitButton);

        expect(axios.post).toHaveBeenCalled();
        expect(axios.post).toHaveBeenCalledWith(expect.any(String), expect.objectContaining({
            sessionToken: "12345",
            star_rating: 1, // Because the first star was clicked
            note: '' // Default value as no text was entered in the textarea
        }));
    });
});

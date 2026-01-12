import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatHistorySearch from '../ChatHistorySearch';

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    clear: () => {
      store = {};
    },
    removeItem: (key) => {
      delete store[key];
    }
  };
})();

global.localStorage = localStorageMock;

// Mock fetch
global.fetch = jest.fn();

describe('ChatHistorySearch Component', () => {
  const mockUserId = 'test_user_123';
  const mockOnClose = jest.fn();
  const mockOnMessageSelect = jest.fn();

  const mockChats = [
    {
      id: 1,
      title: 'Traffic Law Question',
      timestamp: new Date().toISOString(),
      messages: [
        {
          id: 1,
          role: 'user',
          content: 'What are the penalties for speeding?',
          timestamp: new Date()
        },
        {
          id: 2,
          role: 'assistant',
          content: 'Speeding penalties vary by jurisdiction...',
          timestamp: new Date()
        }
      ]
    },
    {
      id: 2,
      title: 'Criminal Law Question',
      timestamp: new Date().toISOString(),
      messages: [
        {
          id: 3,
          role: 'user',
          content: 'What is theft?',
          timestamp: new Date()
        }
      ]
    }
  ];

  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
    global.confirm = jest.fn(() => true);
  });

  test('renders chat history modal', () => {
    render(
      <ChatHistorySearch
        userId={mockUserId}
        onClose={mockOnClose}
        onMessageSelect={mockOnMessageSelect}
      />
    );

    expect(screen.getByText('💬 Chat History')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search your chat history...')).toBeInTheDocument();
  });

  test('loads sessions from localStorage', async () => {
    localStorage.setItem('legubot_chats', JSON.stringify(mockChats));

    render(
      <ChatHistorySearch
        userId={mockUserId}
        onClose={mockOnClose}
        onMessageSelect={mockOnMessageSelect}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Traffic Law Question/i)).toBeInTheDocument();
    });
  });

  test('displays empty state when no chats', async () => {
    render(
      <ChatHistorySearch
        userId={mockUserId}
        onClose={mockOnClose}
        onMessageSelect={mockOnMessageSelect}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('No chat sessions yet')).toBeInTheDocument();
    });
  });

  test('searches through chat history', async () => {
    localStorage.setItem('legubot_chats', JSON.stringify(mockChats));

    render(
      <ChatHistorySearch
        userId={mockUserId}
        onClose={mockOnClose}
        onMessageSelect={mockOnMessageSelect}
      />
    );

    const searchInput = screen.getByPlaceholderText('Search your chat history...');
    const searchButton = screen.getByRole('button', { name: /🔍/i });

    fireEvent.change(searchInput, { target: { value: 'speeding' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText(/penalties for speeding/i)).toBeInTheDocument();
    });
  });

  test('switches between tabs', async () => {
    localStorage.setItem('legubot_chats', JSON.stringify(mockChats));

    render(
      <ChatHistorySearch
        userId={mockUserId}
        onClose={mockOnClose}
        onMessageSelect={mockOnMessageSelect}
      />
    );

    const searchResultsTab = screen.getByText(/Search Results/i);
    fireEvent.click(searchResultsTab);

    expect(searchResultsTab).toHaveClass('active');
  });

  test('deletes a session', async () => {
    localStorage.setItem('legubot_chats', JSON.stringify(mockChats));

    render(
      <ChatHistorySearch
        userId={mockUserId}
        onClose={mockOnClose}
        onMessageSelect={mockOnMessageSelect}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Traffic Law Question/i)).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByTitle('Delete session');
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      const updatedChats = JSON.parse(localStorage.getItem('legubot_chats'));
      expect(updatedChats).toHaveLength(1);
    });
  });

  test('closes modal when close button clicked', () => {
    render(
      <ChatHistorySearch
        userId={mockUserId}
        onClose={mockOnClose}
        onMessageSelect={mockOnMessageSelect}
      />
    );

    const closeButton = screen.getByText('✕');
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  test('handles search with Enter key', async () => {
    localStorage.setItem('legubot_chats', JSON.stringify(mockChats));

    render(
      <ChatHistorySearch
        userId={mockUserId}
        onClose={mockOnClose}
        onMessageSelect={mockOnMessageSelect}
      />
    );

    const searchInput = screen.getByPlaceholderText('Search your chat history...');
    
    fireEvent.change(searchInput, { target: { value: 'theft' } });
    fireEvent.keyPress(searchInput, { key: 'Enter', code: 13, charCode: 13 });

    await waitFor(() => {
      expect(screen.getByText(/What is theft/i)).toBeInTheDocument();
    });
  });

  test('highlights search terms in results', async () => {
    localStorage.setItem('legubot_chats', JSON.stringify(mockChats));

    render(
      <ChatHistorySearch
        userId={mockUserId}
        onClose={mockOnClose}
        onMessageSelect={mockOnMessageSelect}
      />
    );

    const searchInput = screen.getByPlaceholderText('Search your chat history...');
    fireEvent.change(searchInput, { target: { value: 'speeding' } });
    
    const searchButton = screen.getByRole('button', { name: /🔍/i });
    fireEvent.click(searchButton);

    await waitFor(() => {
      const highlighted = screen.getAllByText('speeding');
      expect(highlighted.length).toBeGreaterThan(0);
    });
  });

  test('loads session messages when clicked', async () => {
    localStorage.setItem('legubot_chats', JSON.stringify(mockChats));

    render(
      <ChatHistorySearch
        userId={mockUserId}
        onClose={mockOnClose}
        onMessageSelect={mockOnMessageSelect}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Traffic Law Question/i)).toBeInTheDocument();
    });

    const sessionItem = screen.getByText(/Traffic Law Question/i).closest('.session-item');
    fireEvent.click(sessionItem);

    await waitFor(() => {
      expect(screen.getByText(/penalties for speeding/i)).toBeInTheDocument();
    });
  });
});

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatSidebar from '../ChatSidebar';

describe('ChatSidebar Component', () => {
  const mockChats = [
    {
      id: 1,
      title: 'Traffic Law Question',
      timestamp: new Date().toISOString(),
      messages: [
        { id: 1, role: 'user', content: 'What are speeding penalties?' },
        { id: 2, role: 'assistant', content: 'Penalties vary...' }
      ]
    },
    {
      id: 2,
      title: 'Criminal Law Question',
      timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
      messages: [
        { id: 3, role: 'user', content: 'What is theft?' }
      ]
    }
  ];

  const mockHandlers = {
    onLoadChat: jest.fn(),
    onNewChat: jest.fn(),
    onDeleteChat: jest.fn(),
    onSearchChats: jest.fn(),
    onToggleCollapse: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    global.confirm = jest.fn(() => true);
  });

  test('renders sidebar with chats', () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    expect(screen.getByText('Traffic Law Question')).toBeInTheDocument();
    expect(screen.getByText('Criminal Law Question')).toBeInTheDocument();
  });

  test('displays chat count', () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    expect(screen.getByText('2')).toBeInTheDocument();
  });

  test('filters chats by search query', async () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    const searchInput = screen.getByPlaceholderText('Search chats...');
    fireEvent.change(searchInput, { target: { value: 'traffic' } });

    await waitFor(() => {
      expect(screen.getByText('Traffic Law Question')).toBeInTheDocument();
      expect(screen.queryByText('Criminal Law Question')).not.toBeInTheDocument();
    });
  });

  test('shows empty state when no chats', () => {
    render(
      <ChatSidebar
        savedChats={[]}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    expect(screen.getByText('No chats yet')).toBeInTheDocument();
  });

  test('calls onNewChat when New Chat button clicked', () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    const newChatButton = screen.getByText('New Chat');
    fireEvent.click(newChatButton);

    expect(mockHandlers.onNewChat).toHaveBeenCalled();
  });

  test('calls onLoadChat when chat item clicked', () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    const chatItem = screen.getByText('Traffic Law Question').closest('.chat-item');
    fireEvent.click(chatItem);

    expect(mockHandlers.onLoadChat).toHaveBeenCalledWith(1);
  });

  test('highlights active chat', () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={1}
        {...mockHandlers}
      />
    );

    const chatItem = screen.getByText('Traffic Law Question').closest('.chat-item');
    expect(chatItem).toHaveClass('active');
  });

  test('shows delete button on hover', async () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    const chatItem = screen.getByText('Traffic Law Question').closest('.chat-item');
    fireEvent.mouseEnter(chatItem);

    await waitFor(() => {
      const deleteButton = screen.getByTitle('Delete chat');
      expect(deleteButton).toBeInTheDocument();
    });
  });

  test('calls onDeleteChat when delete button clicked', async () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    const chatItem = screen.getByText('Traffic Law Question').closest('.chat-item');
    fireEvent.mouseEnter(chatItem);

    await waitFor(() => {
      const deleteButton = screen.getByTitle('Delete chat');
      fireEvent.click(deleteButton);
    });

    expect(global.confirm).toHaveBeenCalled();
    expect(mockHandlers.onDeleteChat).toHaveBeenCalledWith(1);
  });

  test('collapses sidebar when toggle clicked', () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        isCollapsed={false}
        {...mockHandlers}
      />
    );

    const toggleButton = screen.getByTitle('Collapse sidebar');
    fireEvent.click(toggleButton);

    expect(mockHandlers.onToggleCollapse).toHaveBeenCalled();
  });

  test('shows collapsed state', () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        isCollapsed={true}
        {...mockHandlers}
      />
    );

    expect(screen.queryByText('Traffic Law Question')).not.toBeInTheDocument();
    expect(screen.getByTitle('Expand sidebar')).toBeInTheDocument();
  });

  test('displays correct timestamp format', () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    // Should show relative time like "Just now" or "1d ago"
    const timestamps = screen.getAllByText(/ago|now/i);
    expect(timestamps.length).toBeGreaterThan(0);
  });

  test('shows message count for each chat', () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    expect(screen.getByText('2 msg')).toBeInTheDocument();
    expect(screen.getByText('1 msg')).toBeInTheDocument();
  });

  test('displays appropriate icons for chat types', () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    const chatIcons = screen.getAllByText(/[⚖️🚗💬👨‍👩‍👧💼🏠]/);
    expect(chatIcons.length).toBeGreaterThan(0);
  });

  test('clears search when clear button clicked', async () => {
    render(
      <ChatSidebar
        savedChats={mockChats}
        currentChatId={null}
        {...mockHandlers}
      />
    );

    const searchInput = screen.getByPlaceholderText('Search chats...');
    fireEvent.change(searchInput, { target: { value: 'traffic' } });

    await waitFor(() => {
      const clearButton = screen.getByRole('button', { name: '' }).closest('.clear-search');
      if (clearButton) {
        fireEvent.click(clearButton);
      }
    });

    expect(searchInput.value).toBe('');
  });
});

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import NavigationBar from '../NavigationBar';

describe('NavigationBar Component', () => {
  const mockHandlers = {
    onNewChat: jest.fn(),
    onSearchChats: jest.fn(),
    onShowImages: jest.fn(),
    onShowApps: jest.fn(),
    onShowCodex: jest.fn(),
    onShowProjects: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders all navigation buttons', () => {
    render(<NavigationBar {...mockHandlers} />);

    expect(screen.getByText('New Chat')).toBeInTheDocument();
    expect(screen.getByText('Search Chats')).toBeInTheDocument();
    expect(screen.getByText('Images')).toBeInTheDocument();
    expect(screen.getByText('Apps')).toBeInTheDocument();
    expect(screen.getByText('Codex')).toBeInTheDocument();
    expect(screen.getByText('Projects')).toBeInTheDocument();
  });

  test('renders LEGID logo', () => {
    render(<NavigationBar {...mockHandlers} />);
    expect(screen.getByText('LEGID')).toBeInTheDocument();
  });

  test('calls onNewChat when New Chat clicked', () => {
    render(<NavigationBar {...mockHandlers} />);
    
    const newChatButton = screen.getByText('New Chat');
    fireEvent.click(newChatButton);

    expect(mockHandlers.onNewChat).toHaveBeenCalledTimes(1);
  });

  test('calls onSearchChats when Search Chats clicked', () => {
    render(<NavigationBar {...mockHandlers} />);
    
    const searchButton = screen.getByText('Search Chats');
    fireEvent.click(searchButton);

    expect(mockHandlers.onSearchChats).toHaveBeenCalledTimes(1);
  });

  test('calls onShowImages when Images clicked', () => {
    render(<NavigationBar {...mockHandlers} />);
    
    const imagesButton = screen.getByText('Images');
    fireEvent.click(imagesButton);

    expect(mockHandlers.onShowImages).toHaveBeenCalledTimes(1);
  });

  test('highlights active view', () => {
    render(<NavigationBar {...mockHandlers} currentView="images" />);
    
    const imagesButton = screen.getByText('Images').closest('button');
    expect(imagesButton).toHaveClass('active');
  });

  test('renders notification icon', () => {
    const { container } = render(<NavigationBar {...mockHandlers} />);
    
    const notificationButton = container.querySelector('[title="Notifications"]');
    expect(notificationButton).toBeInTheDocument();
  });

  test('renders settings icon', () => {
    const { container } = render(<NavigationBar {...mockHandlers} />);
    
    const settingsButton = container.querySelector('[title="Settings"]');
    expect(settingsButton).toBeInTheDocument();
  });

  test('renders profile avatar', () => {
    const { container } = render(<NavigationBar {...mockHandlers} />);
    
    const profileAvatar = container.querySelector('.profile-avatar');
    expect(profileAvatar).toBeInTheDocument();
  });

  test('all buttons have hover effects', () => {
    render(<NavigationBar {...mockHandlers} />);
    
    const newChatButton = screen.getByText('New Chat').closest('button');
    expect(newChatButton).toHaveClass('nav-btn');
  });
});

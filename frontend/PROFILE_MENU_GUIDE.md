# Profile Menu Component - ChatGPT Style

A modern, sleek profile dropdown menu component inspired by ChatGPT's design, featuring a teal gradient avatar, user information display, and a clean menu structure.

## 🎨 Features

- **ChatGPT-style Design**: Modern, clean dropdown menu matching the ChatGPT interface
- **Teal Gradient Avatar**: Beautiful gradient background (#14b8a6 to #0d9488)
- **User Information Display**: Shows username, handle (@username), and subscription tier
- **Plus Tier Badge**: Special badge section for premium users
- **Menu Items**: Upgrade plan, Personalization, Settings, Help, and Log out
- **Smooth Animations**: Dropdown slide-down animation with smooth transitions
- **Dark Theme**: Optimized for dark mode interfaces
- **Responsive**: Works on all screen sizes
- **Accessible**: Keyboard navigation and focus states

## 📁 Files Created

1. **`ProfileMenu.jsx`** - Main React component
2. **`ProfileMenu.css`** - Styling for the component
3. **`profile-menu-demo.html`** - Standalone HTML demo
4. **Updated `NavigationBar.jsx`** - Integration with navigation
5. **Updated `EnhancedApp.jsx`** - App-level integration

## 🚀 Quick Start

### Demo Preview

Open the standalone demo in your browser:

```bash
# Navigate to the frontend directory
cd frontend

# Open the demo file in your browser
# Windows:
start profile-menu-demo.html

# Mac:
open profile-menu-demo.html

# Linux:
xdg-open profile-menu-demo.html
```

### Using in React App

The ProfileMenu component is already integrated into the NavigationBar. To use it:

```jsx
import ProfileMenu from './components/ProfileMenu';

// In your component
<ProfileMenu 
  user={{
    name: 'anshumankush',
    email: 'anshumankush@example.com',
    role: 'plus',
    subscription: 'plus'
  }}
  onLogout={handleLogout}
  onViewChange={handleViewChange}
/>
```

## 🎯 Component Props

### ProfileMenu Props

| Prop | Type | Description |
|------|------|-------------|
| `user` | Object | User data object (name, email, role, subscription) |
| `onLogout` | Function | Callback when logout is clicked |
| `onViewChange` | Function | Callback when menu items are clicked |

### User Object Structure

```javascript
{
  name: 'anshumankush',           // Display name
  email: 'anshumankush@example.com', // User email
  role: 'plus',                   // User role (plus, standard, premium)
  subscription: 'plus'            // Subscription tier
}
```

## 🎨 Customization

### Changing Avatar Colors

Edit `ProfileMenu.css`:

```css
.profile-menu-avatar {
  /* Change the gradient colors here */
  background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
}
```

### Adding Menu Items

Edit `ProfileMenu.jsx`:

```jsx
<button 
  className="profile-menu-item"
  onClick={() => handleMenuItemClick('your-action')}
>
  <svg className="profile-menu-icon" viewBox="0 0 24 24">
    {/* Your icon SVG path */}
  </svg>
  <span>Your Menu Item</span>
</button>
```

### Styling the Dropdown

The dropdown appearance can be customized in `ProfileMenu.css`:

```css
.profile-menu-dropdown {
  width: 290px;              /* Change width */
  background: #2f2f2f;       /* Background color */
  border: 1px solid #3f3f3f; /* Border color */
  border-radius: 12px;       /* Corner radius */
}
```

## 📱 Responsive Behavior

The component automatically adapts to different screen sizes:

- **Desktop**: Full width dropdown with all features
- **Tablet**: Slightly narrower dropdown (280px)
- **Mobile**: Adjusted positioning and padding

## 🎭 Menu Structure

The dropdown menu includes:

1. **Header Section**
   - Large avatar (40px)
   - Display name
   - User handle (@username)

2. **Badge Section** (for Plus users)
   - User info card
   - Subscription tier badge

3. **Menu Items**
   - Upgrade plan
   - Personalization
   - Settings
   - Help (with chevron indicator)
   - Log out

## 🔧 Integration with NavigationBar

The ProfileMenu is integrated into the NavigationBar component:

```jsx
import ProfileMenu from './ProfileMenu';

// In NavigationBar component
<div className="nav-right">
  <button className="nav-icon-btn" title="Notifications">
    {/* Notifications icon */}
  </button>

  <button className="nav-icon-btn" title="Settings">
    {/* Settings icon */}
  </button>

  <ProfileMenu 
    user={user}
    onLogout={onLogout}
    onViewChange={onViewChange}
  />
</div>
```

## 🎬 Animations

The component includes smooth animations:

- **Dropdown**: Slide-down animation (0.2s ease-out)
- **Hover**: Background color transitions (0.15s ease)
- **Icons**: Color transitions on hover

## ♿ Accessibility

- **Keyboard Navigation**: Full keyboard support
- **Focus States**: Visible focus indicators
- **ARIA Labels**: Proper ARIA attributes
- **Screen Readers**: Semantic HTML structure

## 🐛 Troubleshooting

### Dropdown not showing

Check that the parent container has `position: relative` or the dropdown is positioned correctly.

### Styles not applying

Make sure `ProfileMenu.css` is imported:

```jsx
import './ProfileMenu.css';
```

### Avatar not showing initials

Verify the user object has a valid `name` property:

```javascript
user = {
  name: 'John Doe', // Must be present
  email: 'john@example.com'
}
```

## 📝 Example Usage

### Basic Implementation

```jsx
import React, { useState } from 'react';
import ProfileMenu from './components/ProfileMenu';

function App() {
  const [user] = useState({
    name: 'anshumankush',
    email: 'anshumankush@example.com',
    role: 'plus',
    subscription: 'plus'
  });

  const handleLogout = () => {
    console.log('Logging out...');
    // Clear tokens, redirect to login, etc.
  };

  const handleViewChange = (view) => {
    console.log('View changed to:', view);
    // Navigate to different views
  };

  return (
    <div className="app">
      <ProfileMenu 
        user={user}
        onLogout={handleLogout}
        onViewChange={handleViewChange}
      />
    </div>
  );
}
```

### With Dynamic User Data

```jsx
import React, { useState, useEffect } from 'react';
import ProfileMenu from './components/ProfileMenu';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Fetch user data from API
    fetch('/api/profile')
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(err => console.error(err));
  }, []);

  const handleLogout = async () => {
    await fetch('/api/logout', { method: 'POST' });
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  };

  const handleViewChange = (view) => {
    switch (view) {
      case 'upgrade':
        window.location.href = '/upgrade';
        break;
      case 'personalization':
        window.location.href = '/settings/personalization';
        break;
      case 'settings':
        window.location.href = '/settings';
        break;
      case 'help':
        window.open('/help', '_blank');
        break;
    }
  };

  if (!user) return <div>Loading...</div>;

  return (
    <div className="app">
      <ProfileMenu 
        user={user}
        onLogout={handleLogout}
        onViewChange={handleViewChange}
      />
    </div>
  );
}
```

## 🎨 Design Tokens

The component uses these color values:

```css
/* Avatar Gradient */
--avatar-gradient-start: #14b8a6;
--avatar-gradient-end: #0d9488;

/* Background Colors */
--dropdown-bg: #2f2f2f;
--badge-bg: #1f1f1f;
--hover-bg: #3a3a3a;

/* Border Colors */
--border-color: #3f3f3f;

/* Text Colors */
--text-primary: #e5e5e5;
--text-secondary: #a0a0a0;
--text-tertiary: #707070;
```

## 📄 License

This component is part of the LEGID project and follows the project's license.

## 🙏 Acknowledgments

Design inspired by ChatGPT's user interface, adapted for legal AI assistant use case.

---

**Created for**: LEGID - Legal AI Assistant  
**Component Version**: 1.0.0  
**Last Updated**: January 2026

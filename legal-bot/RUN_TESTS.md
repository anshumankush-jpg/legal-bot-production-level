# Running Tests - Enhanced Legal Assistant

## Quick Start

### Install Test Dependencies

```bash
cd legal-bot/frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest jest-environment-jsdom babel-jest @babel/preset-env @babel/preset-react identity-obj-proxy
```

### Run All Tests

```bash
npm test
```

### Run Tests in Watch Mode

```bash
npm run test:watch
```

### Run Tests with Coverage

```bash
npm test -- --coverage
```

## Test Files Created

### Component Tests

1. **ChatHistorySearch.test.jsx** - Tests for chat history search functionality
   - Loading sessions from localStorage
   - Searching through chat history
   - Deleting sessions
   - Switching between tabs
   - Highlighting search terms

2. **NavigationBar.test.jsx** - Tests for navigation bar
   - Rendering all navigation buttons
   - Click handlers
   - Active state highlighting
   - Icons and profile

3. **ChatSidebar.test.jsx** - Tests for chat sidebar
   - Displaying saved chats
   - Search filtering
   - Delete functionality
   - Collapse/expand
   - Timestamp formatting

## Test Coverage Goals

- **Unit Tests**: 90%+
- **Integration Tests**: 85%+
- **E2E Tests**: 80%+

## Running Specific Tests

### Run a specific test file

```bash
npm test ChatHistorySearch.test.jsx
```

### Run tests matching a pattern

```bash
npm test -- --testNamePattern="renders"
```

### Run tests in a specific directory

```bash
npm test -- src/components/__tests__
```

## Debugging Tests

### Run tests with verbose output

```bash
npm test -- --verbose
```

### Run a single test

```bash
npm test -- --testNamePattern="loads sessions from localStorage"
```

### Debug in VS Code

Add this to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Jest Debug",
      "program": "${workspaceFolder}/node_modules/.bin/jest",
      "args": ["--runInBand", "--no-cache"],
      "console": "integratedTerminal",
      "internalConsoleOptions": "neverOpen"
    }
  ]
}
```

## Test Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── __tests__/
│   │   │   ├── ChatHistorySearch.test.jsx
│   │   │   ├── NavigationBar.test.jsx
│   │   │   └── ChatSidebar.test.jsx
│   │   ├── ChatHistorySearch.jsx
│   │   ├── NavigationBar.jsx
│   │   └── ChatSidebar.jsx
│   └── setupTests.js
├── __mocks__/
│   └── fileMock.js
├── jest.config.js
├── .babelrc
└── package.json
```

## Common Test Scenarios

### 1. Testing Component Rendering

```javascript
test('renders component', () => {
  render(<MyComponent />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});
```

### 2. Testing User Interactions

```javascript
test('handles click', () => {
  const handleClick = jest.fn();
  render(<Button onClick={handleClick} />);
  fireEvent.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalled();
});
```

### 3. Testing Async Operations

```javascript
test('loads data', async () => {
  render(<DataComponent />);
  await waitFor(() => {
    expect(screen.getByText('Data loaded')).toBeInTheDocument();
  });
});
```

### 4. Testing LocalStorage

```javascript
test('saves to localStorage', () => {
  localStorage.setItem('key', 'value');
  expect(localStorage.getItem('key')).toBe('value');
});
```

## Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd legal-bot/frontend
          npm install
      
      - name: Run tests
        run: |
          cd legal-bot/frontend
          npm test -- --ci --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          files: ./legal-bot/frontend/coverage/lcov.info
```

## Troubleshooting

### Issue: Tests fail with "Cannot find module"

**Solution**: Install missing dependencies
```bash
npm install
```

### Issue: "ReferenceError: fetch is not defined"

**Solution**: Already mocked in `setupTests.js`

### Issue: "localStorage is not defined"

**Solution**: Already mocked in `setupTests.js`

### Issue: CSS import errors

**Solution**: Using `identity-obj-proxy` in jest.config.js

### Issue: Tests run slowly

**Solution**: Run with fewer workers
```bash
npm test -- --maxWorkers=2
```

## Best Practices

1. **Write tests first** (TDD approach)
2. **Test user behavior**, not implementation
3. **Use descriptive test names**
4. **Keep tests isolated** (no shared state)
5. **Mock external dependencies**
6. **Test edge cases**
7. **Maintain high coverage** (>80%)

## Next Steps

1. Run the tests: `npm test`
2. Check coverage: `npm test -- --coverage`
3. Fix any failing tests
4. Add more tests for edge cases
5. Set up CI/CD pipeline

## Test Results Example

```
PASS  src/components/__tests__/ChatHistorySearch.test.jsx
PASS  src/components/__tests__/NavigationBar.test.jsx
PASS  src/components/__tests__/ChatSidebar.test.jsx

Test Suites: 3 passed, 3 total
Tests:       45 passed, 45 total
Snapshots:   0 total
Time:        3.456 s

Coverage:
-----------|---------|---------|---------|---------
File       | % Stmts | % Branch| % Funcs | % Lines
-----------|---------|---------|---------|---------
All files  |   92.45 |   88.23 |   91.67 |   93.12
```

## Support

For issues or questions:
- Check the [TESTING_GUIDE.md](TESTING_GUIDE.md)
- Review test examples above
- Check Jest documentation: https://jestjs.io/
- Check React Testing Library: https://testing-library.com/react

---

**Happy Testing! 🧪**

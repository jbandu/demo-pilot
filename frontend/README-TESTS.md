# Frontend Tests

Test suite for Demo Copilot frontend using Jest and React Testing Library.

## Prerequisites

1. **Node.js 20+** installed
2. **npm** or **yarn** package manager

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Running Tests

### Run All Tests

```bash
npm test
```

### Run in Watch Mode

```bash
npm run test:watch
```

### Run with Coverage

```bash
npm run test:coverage
```

View coverage report at `coverage/lcov-report/index.html`

### Run Specific Test File

```bash
npm test -- __tests__/page.test.tsx
```

### Update Snapshots

```bash
npm test -- -u
```

## Test Structure

```
__tests__/
└── page.test.tsx              # Homepage tests

jest.config.js                 # Jest configuration
jest.setup.js                  # Test setup and mocks
```

## Writing Tests

### Component Test Example

```typescript
import { render, screen } from '@testing-library/react'
import MyComponent from '@/components/MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

### Async Test Example

```typescript
import { waitFor } from '@testing-library/react'

it('fetches data', async () => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ data: 'test' }),
    })
  ) as jest.Mock

  render(<MyComponent />)

  await waitFor(() => {
    expect(screen.getByText('test')).toBeInTheDocument()
  })
})
```

## Available Mocks

Configured in `jest.setup.js`:

- **WebSocket**: Mocked for testing real-time features
- **fetch**: Mocked for API calls

## Common Issues

### Cannot find module '@/components/...'

Ensure paths are correct in `jest.config.js` moduleNameMapper.

### TextEncoder is not defined

Add to `jest.setup.js`:
```javascript
global.TextEncoder = require('util').TextEncoder
global.TextDecoder = require('util').TextDecoder
```

### Test runs but component not found

Make sure the component files exist and paths are correct.

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run frontend tests
  run: |
    cd frontend
    npm install
    npm test -- --coverage
```

## Coverage Goals

- **Components**: >80% coverage
- **Pages**: >90% coverage
- **Utils**: >85% coverage
- **Overall**: >80% coverage

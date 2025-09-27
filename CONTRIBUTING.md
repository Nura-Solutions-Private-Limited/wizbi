# Contributing to Wizbi

We welcome contributions to Wizbi! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful, inclusive, and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/wizbi.git
   cd wizbi
   ```
3. **Add the upstream repository** as a remote:
   ```bash
   git remote add upstream https://github.com/Nura-Solutions-Private-Limited/wizbi.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- PostgreSQL
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   ```

4. Start the development server:
   ```bash
   npm start
   ```

## Contribution Guidelines

### Before You Start

1. **Check existing issues** to see if your contribution is already being worked on
2. **Create an issue** for new features or bugs before starting work
3. **Wait for approval** on feature requests before implementing
4. **Keep changes focused** - one feature or fix per pull request

### Types of Contributions

- **Bug fixes**: Always welcome with proper testing
- **Feature additions**: Please discuss in an issue first
- **Documentation improvements**: Very much appreciated
- **Code quality improvements**: Refactoring, performance optimizations
- **Tests**: Additional test coverage is always helpful

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/user-authentication`
- `bugfix/api-response-format`
- `docs/contributing-guide`

### 2. Make Your Changes

- Follow the coding standards outlined below
- Write or update tests as needed
- Update documentation if necessary
- Ensure all tests pass locally

### 3. Commit Your Changes

Use conventional commit messages:

```bash
git commit -m "feat: add user authentication endpoint"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update API documentation"
```

Commit message format:
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `style:` code formatting (no code changes)
- `refactor:` code refactoring
- `test:` adding or updating tests
- `chore:` maintenance tasks

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

1. Go to GitHub and create a pull request
2. Fill out the pull request template completely
3. Link any related issues
4. Request review from maintainers

### 5. Pull Request Requirements

✅ **Required for all PRs:**
- [ ] Descriptive title and description
- [ ] All CI checks pass
- [ ] Code follows project standards
- [ ] Tests added/updated as needed
- [ ] Documentation updated if necessary
- [ ] No merge conflicts
- [ ] Approved by at least one maintainer

## Coding Standards

### Backend (Python)

- **Formatter**: Use `ruff` for code formatting
- **Linting**: Code must pass `ruff` linting
- **Type hints**: Use type hints for all function parameters and returns
- **Docstrings**: Include docstrings for all public functions and classes
- **Naming**: Use snake_case for variables and functions, PascalCase for classes

Example:
```python
def create_user(user_data: UserCreate) -> User:
    """Create a new user in the database.
    
    Args:
        user_data: User creation data
        
    Returns:
        Created user instance
        
    Raises:
        ValidationError: If user data is invalid
    """
    # Implementation here
```

### Frontend (TypeScript/React)

- **Formatter**: Use `eslint` and `prettier`
- **Naming**: Use camelCase for variables and functions, PascalCase for components
- **Components**: Use functional components with TypeScript
- **Props**: Always define prop types with interfaces
- **Hooks**: Follow React hooks best practices

Example:
```typescript
interface UserProfileProps {
  user: User;
  onUpdate: (user: User) => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ user, onUpdate }) => {
  // Component implementation
};
```

### Code Quality Tools

Run these commands before submitting:

**Backend:**
```bash
cd backend
ruff check .
ruff format .
pytest
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run type-check
npm test
```

## Testing

### Backend Testing

- Write tests for all API endpoints
- Use pytest fixtures for database setup
- Mock external dependencies
- Aim for >80% code coverage

```python
def test_create_user_success(client, db_session):
    user_data = {"email": "test@example.com", "password": "testpass123"}
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

### Frontend Testing

- Write unit tests for components
- Test user interactions
- Use React Testing Library
- Test API integration points

```typescript
test('renders user profile correctly', () => {
  const user = { id: 1, name: 'John Doe', email: 'john@example.com' };
  render(<UserProfile user={user} onUpdate={jest.fn()} />);
  expect(screen.getByText('John Doe')).toBeInTheDocument();
});
```

## Documentation

### API Documentation

- All API endpoints must be documented with OpenAPI/Swagger
- Include example requests and responses
- Document error cases and status codes

### Code Documentation

- Write clear, concise comments for complex logic
- Update README.md for significant changes
- Include setup instructions for new dependencies

### Commit Documentation

- Reference issue numbers in commits: `fixes #123`
- Include breaking change notes in commit messages
- Document migration steps for database changes

## Review Process

### What Reviewers Look For

1. **Functionality**: Does the code work as intended?
2. **Code Quality**: Is the code clean, readable, and maintainable?
3. **Testing**: Are there adequate tests with good coverage?
4. **Security**: Are there any security vulnerabilities?
5. **Performance**: Will this impact application performance?
6. **Documentation**: Is the code and changes well documented?

### Addressing Review Feedback

- Respond to all reviewer comments
- Ask questions if feedback is unclear
- Make requested changes promptly
- Re-request review after addressing feedback

## Release Process

This project follows semantic versioning (SemVer):

- **Major version** (1.0.0): Breaking changes
- **Minor version** (0.1.0): New features, backward compatible
- **Patch version** (0.0.1): Bug fixes, backward compatible

## Getting Help

- **Questions about contributing**: Open a discussion on GitHub
- **Bug reports**: Create an issue with the bug template
- **Feature requests**: Create an issue with the feature template
- **General help**: Check existing documentation or ask in discussions

## Recognition

Contributors will be recognized in our CONTRIBUTORS.md file and release notes. We appreciate all forms of contribution, whether it's code, documentation, testing, or community support.

Thank you for contributing to Wizbi! 🚀
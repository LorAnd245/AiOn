# Contributing to AION

Thank you for your interest in contributing to AION! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Screenshots** if applicable
- **Environment details** (OS, Python version, Node version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** - why is this enhancement needed?
- **Proposed solution** - how should it work?
- **Alternatives considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards below
3. **Add tests** if you've added code that should be tested
4. **Update documentation** if you've changed APIs or added features
5. **Ensure tests pass** by running `pytest` in the backend directory
6. **Commit your changes** with clear, descriptive commit messages
7. **Push to your fork** and submit a pull request

#### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Write clear PR descriptions explaining what and why
- Reference related issues using `#issue-number`
- Ensure CI checks pass before requesting review
- Respond to review feedback promptly

## Development Setup

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov  # Development dependencies
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

**Example:**

```python
async def create_agent(
    agent_data: AgentCreate,
    user_id: int,
    db: AsyncSession
) -> Agent:
    """
    Create a new AI agent.
    
    Args:
        agent_data: Agent creation data
        user_id: ID of the user creating the agent
        db: Database session
        
    Returns:
        Created agent instance
        
    Raises:
        ValueError: If agent name is already taken
    """
    # Implementation here
    pass
```

### JavaScript/React (Frontend)

- Use ESLint configuration provided
- Use functional components with hooks
- Keep components small and focused
- Use meaningful component and variable names
- Add PropTypes or TypeScript types

**Example:**

```jsx
import { useState, useEffect } from 'react';

export function AgentCard({ agent, onSelect }) {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleClick = async () => {
    setIsLoading(true);
    try {
      await onSelect(agent.id);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="agent-card" onClick={handleClick}>
      {/* Component content */}
    </div>
  );
}
```

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and PRs when relevant

**Examples:**

```
Add user profile editing functionality

Implement RAG confidence scoring
- Add confidence calculation to rag_engine.py
- Update chat response to include confidence scores
- Add tests for confidence scoring
Fixes #123

Fix authentication token refresh bug
```

## Project Structure

### Backend Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI application
│   ├── models.py         # SQLAlchemy models
│   ├── auth.py           # Authentication logic
│   ├── database.py       # Database configuration
│   ├── config.py         # Application settings
│   ├── rag_engine.py     # RAG implementation
│   └── routes/           # API route handlers
│       ├── auth.py
│       ├── users.py
│       ├── agents.py
│       ├── chat.py
│       └── stats.py
├── tests/                # Test suite
├── alembic/              # Database migrations
└── requirements.txt      # Python dependencies
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/       # Reusable components
│   │   ├── layout/      # Layout components
│   │   └── ui/          # UI components
│   ├── pages/           # Page components
│   ├── context/         # React context
│   ├── services/        # API services
│   └── main.jsx         # Application entry
├── public/              # Static assets
└── package.json         # Node dependencies
```

## Database Migrations

When making changes to database models:

1. Update models in `backend/app/models.py`
2. Create a migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of changes"
   ```
3. Review the generated migration in `backend/alembic/versions/`
4. Test the migration:
   ```bash
   alembic upgrade head
   ```
5. Include the migration file in your PR

## Testing Guidelines

### Backend Tests

- Write tests for all new features
- Test both success and error cases
- Use fixtures for common test data
- Mock external dependencies (API calls, etc.)
- Aim for >80% code coverage

**Example:**

```python
import pytest
from app.models import User

@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test user creation with valid data."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"
```

### Frontend Tests

- Test component rendering
- Test user interactions
- Test API integration
- Use React Testing Library

## Documentation

- Update README.md for user-facing changes
- Update API documentation for endpoint changes
- Add inline comments for complex logic
- Update CHANGELOG.md with notable changes

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with the `question` label
- Reach out to maintainers

Thank you for contributing to AION! 🚀

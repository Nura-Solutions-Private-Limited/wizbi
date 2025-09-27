# Wizbi - Full Stack Application Template

![CI Status](https://github.com/Nura-Solutions-Private-Limited/wizbi/workflows/CI/badge.svg)
![Code Quality](https://github.com/Nura-Solutions-Private-Limited/wizbi/workflows/Code%20Quality/badge.svg)
![License](https://img.shields.io/github/license/Nura-Solutions-Private-Limited/wizbi)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-16+-green.svg)

A modern, production-ready template for building full-stack applications with **FastAPI** backend and **React** frontend. This template includes comprehensive CI/CD pipelines, code quality tools, and development best practices.

## 🚀 Features

### Backend (FastAPI)
- ⚡ **FastAPI** with automatic API documentation
- 🗄️ **SQLAlchemy** ORM with PostgreSQL support
- 📦 **Alembic** for database migrations
- 🔒 **Pydantic** for data validation
- 🧪 **Pytest** for testing with coverage
- 🔍 **Ruff** for linting and code formatting
- 🛡️ **Security** scanning with Bandit

### Frontend (React)
- ⚛️ **React 18** with TypeScript
- 🎨 **Modern CSS** with responsive design
- 🧭 **React Router** for navigation
- 📡 **Axios** for API communication
- 🧪 **Jest & React Testing Library** for testing
- 🔍 **ESLint & Prettier** for code quality

### DevOps & CI/CD
- 🔄 **GitHub Actions** for CI/CD
- 🐳 **Docker** support with multi-stage builds
- 🔒 **Security scanning** with multiple tools
- 📊 **Code coverage** reporting
- 🏷️ **Semantic versioning** and automated releases
- 🚢 **Automated deployments** to staging and production

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **PostgreSQL 12+**
- **Docker** (optional, for containerized development)
- **Git**

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Nura-Solutions-Private-Limited/wizbi.git
cd wizbi
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database configuration

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- 🌐 **API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 🔍 **ReDoc**: http://localhost:8000/redoc

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env

# Start the development server
npm start
```

The frontend will be available at http://localhost:3000

## 🏗️ Project Structure

```
wizbi/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core configuration
│   │   └── __init__.py
│   ├── alembic/           # Database migrations
│   ├── tests/             # Backend tests
│   ├── requirements.txt   # Python dependencies
│   └── main.py           # FastAPI app entry point
├── frontend/               # React frontend
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── App.tsx       # Main app component
│   │   └── index.tsx     # Entry point
│   ├── public/           # Static assets
│   ├── package.json      # Node.js dependencies
│   └── tsconfig.json     # TypeScript configuration
├── .github/               # GitHub workflows and templates
│   ├── workflows/        # CI/CD workflows
│   └── CODEOWNERS       # Code ownership rules
├── docs/                 # Documentation
├── CONTRIBUTING.md       # Contribution guidelines
└── README.md            # This file
```

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v
```

### Frontend Testing

```bash
cd frontend

# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Run tests in CI mode
npm run test:ci
```

## 🔍 Code Quality

### Backend Code Quality

```bash
cd backend

# Lint code
ruff check .

# Format code
ruff format .

# Type checking
mypy . --ignore-missing-imports

# Security scanning
bandit -r . -ll
```

### Frontend Code Quality

```bash
cd frontend

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Type checking
npm run type-check

# Format code
npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"
```

## 🐳 Docker Development

### Using Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Docker Builds

```bash
# Backend
cd backend
docker build -t wizbi-backend .

# Frontend
cd frontend
docker build -t wizbi-frontend .
```

## 🚀 Deployment

### Environment Setup

1. **Staging**: Automatically deploys from `develop` branch
2. **Production**: Automatically deploys from `main` branch

### Manual Deployment

```bash
# Deploy to staging
git push origin develop

# Deploy to production
git push origin main
```

### Environment Variables

Ensure these environment variables are configured in your deployment environment:

#### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `REDIS_URL`: Redis connection string (optional)

#### Frontend
- `REACT_APP_API_URL`: Backend API URL

## 📊 Monitoring and Observability

- **Health Checks**: `/api/v1/health/` endpoint
- **Metrics**: Integrated with CI/CD pipelines
- **Logging**: Structured logging with correlation IDs
- **Error Tracking**: Ready for Sentry integration

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `npm test` and `pytest`
5. Run code quality checks
6. Commit your changes: `git commit -m 'feat: add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Review Process

- All changes require a pull request
- Minimum 1 approval required
- All CI checks must pass
- Code must follow our style guidelines

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Branch Protection](docs/BRANCH_PROTECTION.md) - Git workflow rules
- [Deployment Guide](docs/DEPLOYMENT.md) - Deployment instructions

## 🔒 Security

- Regular dependency updates via Dependabot
- Security scanning in CI/CD pipeline
- Code scanning with CodeQL
- Secrets scanning enabled

To report security vulnerabilities, please email security@nura-solutions.com

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Backend Team**: [@backend-team](https://github.com/orgs/Nura-Solutions-Private-Limited/teams/backend-team)
- **Frontend Team**: [@frontend-team](https://github.com/orgs/Nura-Solutions-Private-Limited/teams/frontend-team)
- **DevOps Team**: [@devops-team](https://github.com/orgs/Nura-Solutions-Private-Limited/teams/devops-team)

## 🆘 Support

- 📧 **Email**: support@nura-solutions.com
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Nura-Solutions-Private-Limited/wizbi/discussions)
- 🐛 **Issues**: [GitHub Issues](https://github.com/Nura-Solutions-Private-Limited/wizbi/issues)

## 🎯 Roadmap

- [ ] Authentication & Authorization system
- [ ] Real-time features with WebSockets
- [ ] API rate limiting
- [ ] GraphQL API support
- [ ] Mobile app with React Native
- [ ] Microservices architecture support
- [ ] Advanced monitoring and alerting

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing Python web framework
- [React](https://reactjs.org/) for the frontend library
- [GitHub Actions](https://github.com/features/actions) for CI/CD
- All our contributors and the open-source community

---

**Happy coding! 🚀**
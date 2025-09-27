import React from 'react';

const Home: React.FC = () => {
  return (
    <div>
      <h2>Home Page</h2>
      <p>Welcome to the Wizbi application. This is a template for a full-stack application with FastAPI backend and React frontend.</p>
      
      <div style={{ marginTop: '2rem' }}>
        <h3>Getting Started</h3>
        <ul style={{ textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>
          <li>Backend API is running on FastAPI with Alembic for database migrations</li>
          <li>Frontend is built with React and TypeScript</li>
          <li>API health status is displayed in the header</li>
          <li>Check the documentation for development setup</li>
        </ul>
      </div>
    </div>
  );
};

export default Home;
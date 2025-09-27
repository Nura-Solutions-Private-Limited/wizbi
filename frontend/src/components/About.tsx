import React from 'react';

const About: React.FC = () => {
  return (
    <div>
      <h2>About Wizbi</h2>
      <p>
        Wizbi is a template repository for building full-stack applications with modern technologies.
      </p>
      
      <div style={{ marginTop: '2rem' }}>
        <h3>Technology Stack</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div>
            <h4>Backend</h4>
            <ul style={{ textAlign: 'left' }}>
              <li>FastAPI</li>
              <li>SQLAlchemy</li>
              <li>Alembic</li>
              <li>PostgreSQL</li>
              <li>Pydantic</li>
            </ul>
          </div>
          <div>
            <h4>Frontend</h4>
            <ul style={{ textAlign: 'left' }}>
              <li>React</li>
              <li>TypeScript</li>
              <li>React Router</li>
              <li>Axios</li>
              <li>ESLint</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
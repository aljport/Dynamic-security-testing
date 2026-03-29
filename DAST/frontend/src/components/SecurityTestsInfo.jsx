import React from 'react';
import './SecurityTestsInfo.css';

const SecurityTests = () => {
  const securityTests = [
    {
      id: 1,
      name: "SQL Injection",
      description: "Detects vulnerabilities where malicious SQL code can be injected into database queries."
    },
    {
      id: 2,
      name: "XSS (Cross-Site Scripting)",
      description: "Identifies areas where attackers could inject malicious scripts into web pages viewed by users."
    },
    {
      id: 3,
      name: "Broken Authentication",
      description: "Tests for weak authentication mechanisms that could allow unauthorized access."
    },
    {
      id: 4,
      name: "Open Directories",
      description: "Scans for publicly accessible directories that may expose sensitive files or information."
    }
  ];

  return (
    <div className='app-information'>
      <h2 className='info-section-title'>Security Tests Performed</h2>
      <div className='test-boxes-container'>
        {securityTests.map((test) => (
          <div key={test.id} className='test-box'>
            <h3 className='test-name'>{test.name}</h3>
            <p className='test-description'>{test.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SecurityTests;

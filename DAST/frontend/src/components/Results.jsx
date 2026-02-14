import React from 'react';
import './Results.css';

const Results = () => {
  return (
    <div className='results'>
          <p className='results-title'>Results</p>
          <div className='results-box'>
            <p className='results-text'>Scan successful. No security vulnerabilites found.</p>
          </div>
    </div>
  );
};

export default Results;

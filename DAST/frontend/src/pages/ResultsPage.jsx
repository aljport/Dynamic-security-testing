import { useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import './ResultsPage.css';

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { url, scanResults } = location.state || {};
  const [showAllFindings, setShowAllFindings] = useState(false);

  if (!url || !scanResults) {
    return (
      <div className="results-container">
        <div className="error-message">
          <h1>No Scan Results</h1>
          <p>Please scan a URL first.</p>
          <button onClick={() => navigate('/')}>Go Back to Scanner</button>
        </div>
      </div>
    );
  }

  const { scan_summary, vulnerabilities } = scanResults;
  const sqlFindings = vulnerabilities.sql_injection.findings || [];
  const hasMoreFindings = sqlFindings.length > 3;
  const displayedFindings = showAllFindings ? sqlFindings : sqlFindings.slice(0, 3);
  const cookies = vulnerabilities.broken_authentication.cookies

  return (
    <div className="results-page">
      {/* Header Section */}
      <div className="results-header-section">
        <button className="back-button" onClick={() => navigate('/')}>
          ←
        </button>
      </div>

      {/* Main Container */}
      <div className="results-container">
        {/* Title and URL */}
        <div className="results-title-card">
          <h1>Results Dashboard</h1>
          <p className="scanned-url-text">Scanned URL: {url}</p>
        </div>

        {/* Status Icon/Image Placeholder */}
        <div className="status-icon-container">
          <div className="status-icon-placeholder">
            {scan_summary.safe ? '✅' : '⚠️'}
          </div>
        </div>

        {/* Vulnerabilities Found Section */}
        <div className="vulnerabilities-found-card">
          <h2>Vulnerabilities Found: {scan_summary.threats_found}</h2>
          <div className="vulnerability-badges">
            {scan_summary.threat_categories.map((category, index) => (
              <button 
                key={index} 
                className={`vulnerability-badge ${category === 'None' ? 'none-badge' : 'threat-badge'}`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* XSS Section */}
        <div className="vulnerability-detail-card">
          <h2>Cross-Site Scripting (XSS)</h2>
          <div className="vulnerability-content">
            {vulnerabilities.xss.vulnerable ? (
              <>
                <div className="vuln-info-row">
                  <span className="vuln-label">Status:</span>
                  <span className="vuln-value vulnerable-text">Vulnerable</span>
                </div>
                <div className="vuln-info-row">
                  <span className="vuln-label">Type:</span>
                  <span className="vuln-value">{vulnerabilities.xss.type}</span>
                </div>
                <div className="vuln-info-row">
                  <span className="vuln-label">Method:</span>
                  <span className="vuln-value">{vulnerabilities.xss.method}</span>
                </div>
                <div className="vuln-info-row">
                  <span className="vuln-label">Detail:</span>
                  <span className="vuln-value">{vulnerabilities.xss.detail}</span>
                </div>
              </>
            ) : (
              <div className="vuln-info-row">
                <span className="vuln-label">Status:</span>
                <span className="vuln-value safe-text">No vulnerabilities detected</span>
              </div>
            )}
          </div>
        </div>

        {/* SQL Injection Section */}
        <div className="vulnerability-detail-card">
          <h2>SQL-Injection</h2>
          <div className="vulnerability-content">
            {vulnerabilities.sql_injection.vulnerable ? (
              <>
                <div className="vuln-info-row">
                  <span className="vuln-label">Status:</span>
                  <span className="vuln-value vulnerable-text">Vulnerable</span>
                </div>
                <div className="vuln-info-row">
                  <span className="vuln-label">Findings:</span>
                  <span className="vuln-value">{vulnerabilities.sql_injection.findings_count} potential injection point(s)</span>
                </div>
                
                {/* Show findings details */}
                <div className="findings-section">
                  {displayedFindings.map((finding, index) => (
                    <div key={index} className="finding-detail">
                      <p><strong>Finding #{index + 1}:</strong> {finding.type}</p>
                      <p><strong>URL:</strong> {finding.url}</p>
                      {finding.parameter && <p><strong>Parameter:</strong> {finding.parameter}</p>}
                      {finding.payload && <p><strong>Payload:</strong> <code>{finding.payload}</code></p>}
                      {finding.similarity && <p><strong>Similarity:</strong> {finding.similarity}</p>}
                      {finding.delay && <p><strong>Delay:</strong> {finding.delay}s</p>}
                    </div>
                  ))}
                  
                  {/* Show More/Less Button */}
                  {hasMoreFindings && (
                    <button 
                      className="show-more-button"
                      onClick={() => setShowAllFindings(!showAllFindings)}
                    >
                      {showAllFindings ? (
                        <>
                          <span>Show Less</span>
                          <span className="arrow arrow-up">▲</span>
                        </>
                      ) : (
                        <>
                          <span>Show More Findings</span>
                          <span className="arrow arrow-down">▼</span>
                        </>
                      )}
                    </button>
                  )}
                </div>
              </>
            ) : (
              <div className="vuln-info-row">
                <span className="vuln-label">Status:</span>
                <span className="vuln-value safe-text">No vulnerabilities detected</span>
              </div>
            )}
          </div>
        </div>

        {/* Broken Authentication Section */}
        <div className="vulnerability-detail-card">
          <h2>Broken Authentication</h2>
          <div className="vulnerability-content">
            {vulnerabilities.sql_injection.vulnerable ? (
              <>
                <div className="vuln-info-row">
                  <span className="vuln-label">Status:</span>
                  <span className="vuln-value vulnerable-text">Vulnerable</span>
                </div>
                <div className="vuln-info-row">
                  <span className="vuln-label">Findings:</span>
                  <span className="vuln-value">{vulnerabilities.broken_authentication.findings_count} vulnerabilities</span>
                </div>
                
                {/* Show findings details */}
                  <div className="findings-section">
                  {cookies.map((cookie, index) => (
                    <div key={index} className="finding-detail">
                      <p><strong>Finding #{index + 1}:</strong> Cookies</p>
                      <p><strong>Vulnerability:</strong> {cookie}</p>
                    </div>
                    ))}
                  </div>
              </>
            ) : (
              <div className="vuln-info-row">
                <span className="vuln-label">Status:</span>
                <span className="vuln-value safe-text">No vulnerabilities detected</span>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

export default ResultsPage;
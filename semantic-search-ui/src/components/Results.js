import React from 'react';

const Results = ({ results }) => {
  const { documents, summary } = results;

  return (
    <div className="results">
      {documents.length > 0 && (
        <div className="documents">
          <h3>Top Documents</h3>
          <ul>
            {documents.map((doc, index) => (
              <li key={index}>
                <p><strong>Document {index + 1}:</strong></p>
                <div style={{ whiteSpace: 'pre-wrap', marginBottom: '10px' }}>
                  {/* Split the document content and render each part in a readable way */}
                  {doc.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {summary && (
        <div className="summary">
          <h3>Summary</h3>
          {/* Display summary with newlines respected */}
          <div style={{ whiteSpace: 'pre-wrap' }}>{summary}</div>
        </div>
      )}
    </div>
  );
};

export default Results;
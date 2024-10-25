import React, { useState, useEffect } from 'react';

const Results = ({ results }) => {
  const { documents = [], summary = "" } = results; // Use default values in case of undefined
  const docsPerPage = 10; // Number of documents to show per page
  const [currentPage, setCurrentPage] = useState(1);

  // Debugging: Log results to verify structure
  useEffect(() => {
    console.log("Results received:", results);
  }, [results]);

  // Check if documents exist and sort by score
  const sortedDocuments = documents.length ? [...documents].sort((a, b) => (b.score || 0) - (a.score || 0)) : [];

  // Calculate the range of documents to display based on the current page
  const startIndex = (currentPage - 1) * docsPerPage;
  const endIndex = startIndex + docsPerPage;
  const currentDocs = sortedDocuments.slice(startIndex, endIndex);

  // Total pages based on document count and docsPerPage
  const totalPages = Math.ceil(documents.length / docsPerPage);

  // Handle page changes
  const goToPage = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  return (
    <div className="results">
      {/* Render summary at the top */}
      {summary && (
        <div className="summary">
          <h3>Summary</h3>
          <div style={{ whiteSpace: 'pre-wrap' }}>{summary}</div>
        </div>
      )}

      {/* Render paginated documents */}
      {sortedDocuments.length > 0 ? (
        <div className="documents">
          <h3>Top Documents</h3>
          <ul>
            {currentDocs.map((doc, index) => (
              <li key={index}>
                <p><strong>Document {startIndex + index + 1}:</strong></p>
                <p><strong>Score:</strong> {doc.score ? doc.score.toFixed(4) : "N/A"}</p> {/* Display document score */}
                <div style={{ whiteSpace: 'pre-wrap', marginBottom: '10px' }}>
                  {/* Ensure doc.text is a string before calling split */}
                  {(typeof doc.text === 'string' ? doc.text : "").split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                </div>
              </li>
            ))}
          </ul>

          {/* Pagination Controls */}
          <div className="pagination">
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                onClick={() => goToPage(i + 1)}
                disabled={currentPage === i + 1}
                style={{
                  margin: '0 5px',
                  padding: '5px 10px',
                  cursor: currentPage === i + 1 ? 'default' : 'pointer',
                }}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <p>No documents found.</p> // Fallback message
      )}
    </div>
  );
};

export default Results;
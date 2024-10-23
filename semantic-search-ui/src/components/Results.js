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
                <p>{doc}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {summary && (
        <div className="summary">
          <h3>Summary</h3>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
};

export default Results;

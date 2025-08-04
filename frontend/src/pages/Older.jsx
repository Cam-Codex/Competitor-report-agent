import React from 'react';
import Section from '../components/Section.jsx';

export default function Older({ articles }) {
  const grouped = articles.reduce((acc, art) => {
    const vendor = art.source || 'Unknown';
    (acc[vendor] = acc[vendor] || []).push(art);
    return acc;
  }, {});

  return (
    <div className="vendor-folders">
      {Object.entries(grouped).map(([vendor, arts]) => (
        <details key={vendor}>
          <summary>{vendor}</summary>
          <Section articles={arts} />
        </details>
      ))}
    </div>
  );
}


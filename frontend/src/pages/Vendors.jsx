import React from 'react';
import Section from '../components/Section.jsx';

export default function Vendors({ articles }) {
  const vendors = articles.filter((a) => a.category === 'vendor');
  const grouped = vendors.reduce((acc, art) => {
    (acc[art.source] = acc[art.source] || []).push(art);
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

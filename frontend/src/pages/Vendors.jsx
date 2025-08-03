import React from 'react';
import Section from '../components/Section.jsx';

export default function Vendors({ articles }) {
  const vendors = articles.filter((a) => a.category === 'vendor');
  const grouped = vendors.reduce((acc, art) => {
    (acc[art.source] = acc[art.source] || []).push(art);
    return acc;
  }, {});

  return (
    <div>
      {Object.entries(grouped).map(([vendor, arts]) => (
        <Section key={vendor} title={vendor} articles={arts} />
      ))}
    </div>
  );
}

import React from 'react';
import Section from '../components/Section.jsx';

export default function Older({ articles }) {
  const grouped = articles.reduce((acc, art) => {
    const date = art.fetched || 'Unknown';
    (acc[date] = acc[date] || []).push(art);
    return acc;
  }, {});

  return (
    <div>
      {Object.entries(grouped).map(([date, arts]) => (
        <Section key={date} title={date} articles={arts} />
      ))}
    </div>
  );
}

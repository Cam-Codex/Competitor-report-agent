import React from 'react';
import Section from '../components/Section.jsx';

export default function Home({ articles }) {
  const latest = articles.slice(0, 5);
  return (
    <div>
      <Section title="Latest" articles={latest} />
    </div>
  );
}

import React from 'react';
import Section from '../components/Section.jsx';

export default function Industry({ articles }) {
  const industry = articles.filter((a) => a.category === 'industry');
  return <Section title="Industry" articles={industry} />;
}

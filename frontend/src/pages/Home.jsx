import React from 'react';
import Section from '../components/Section.jsx';

export default function Home({ articles }) {
  return (
    <div>
      <Section title="Latest" articles={articles} />
    </div>
  );
}

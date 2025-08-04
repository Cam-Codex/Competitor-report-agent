import React from 'react';
import Section from '../components/Section.jsx';

export default function Home({ articles }) {
  if (!articles.length) {
    return <p className="empty">No articles available.</p>;
  }

  const priority = [
    'Databricks',
    'Snowflake',
    'Microsoft',
    'Sigma Computing',
    'Salesforce',
    'Qlik',
    'Looker',
    'Google',
    'OpenAI',
    'Anthropic',
    'Tableau',
  ];
  const prioritySet = new Set(priority);

  const sorted = [...articles].sort((a, b) => {
    const aPri = prioritySet.has(a.source);
    const bPri = prioritySet.has(b.source);
    if (aPri !== bPri) return bPri - aPri;
    return new Date(b.fetched || 0) - new Date(a.fetched || 0);
  });

  const topTen = sorted.slice(0, 10);
  const top = topTen.filter((a) => prioritySet.has(a.source));
  const rest = topTen.filter((a) => !prioritySet.has(a.source));

  return (
    <div className="home">
      {top.length > 0 && <Section title="Top News" articles={top} />}
      {rest.length > 0 && <Section title="Latest" articles={rest} />}
    </div>
  );
}

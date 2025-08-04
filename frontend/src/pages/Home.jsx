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
  const top = articles.filter((a) => priority.includes(a.source));
  const rest = articles.filter((a) => !priority.includes(a.source));

  return (
    <div className="home">
      {top.length > 0 && <Section title="Top News" articles={top} />}
      <Section title="Latest" articles={rest} />
    </div>
  );
}

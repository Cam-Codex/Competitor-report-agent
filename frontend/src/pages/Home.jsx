import React from 'react';
import Section from '../components/Section.jsx';

export default function Home({ articles }) {
  const priority = [
    'Databricks',
    'Snowflake',
    'Microsoft',
    'Sigma Computing',
    'Salesforce',
    'Qlik',
    'Looker',
    'Google',
  ];
  const top = articles.filter((a) => priority.includes(a.source));
  const rest = articles.filter((a) => !priority.includes(a.source));

  return (
    <div>
      {top.length > 0 && <Section title="Top News" articles={top} />}
      <Section title="Latest" articles={rest} />
    </div>
  );
}

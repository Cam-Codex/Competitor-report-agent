import React, { useState } from 'react';
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
    'Pyramid Analytics',
  ];
  const top = articles.filter((a) => priority.includes(a.source));
  const rest = articles.filter((a) => !priority.includes(a.source));
  const defaultTab = top.length > 0 ? 'top' : 'latest';
  const [tab, setTab] = useState(defaultTab);
  const shown = tab === 'top' ? top : rest;

  return (
    <div>
      <div className="tabs">
        {top.length > 0 && (
          <button
            className={tab === 'top' ? 'active' : ''}
            onClick={() => setTab('top')}
          >
            Top News
          </button>
        )}
        <button
          className={tab === 'latest' ? 'active' : ''}
          onClick={() => setTab('latest')}
        >
          Latest News
        </button>
      </div>
      <Section
        title={tab === 'top' ? 'Top News' : 'Latest News'}
        articles={shown}
      />
    </div>
  );
}

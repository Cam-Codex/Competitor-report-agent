import React, { useEffect, useState } from 'react';

function Section({ title, articles }) {
  if (!articles.length) return null;
  return (
    <section>
      <h2>{title}</h2>
      {articles.map((art) => (
        <article key={art.link}>
          <h3>
            <a href={art.link} target="_blank" rel="noopener noreferrer">
              {art.title}
            </a>
          </h3>
          {art.published && <p><em>{art.published}</em></p>}
          {art.summary && <p>{art.summary}</p>}
          {art.drawbacks && (
            <p><strong>Potential drawbacks:</strong> {art.drawbacks}</p>
          )}
        </article>
      ))}
    </section>
  );
}

export default function App() {
  const [articles, setArticles] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    fetch('/articles.json')
      .then((res) => res.json())
      .then(setArticles)
      .catch(() => setArticles([]));
  }, []);

  const filtered = articles.filter((a) => {
    const text = `${a.title} ${a.summary}`.toLowerCase();
    return text.includes(query.toLowerCase());
  });

  const vendors = filtered.filter((a) => a.category === 'vendor');
  const vendorSections = vendors.reduce((acc, art) => {
    (acc[art.source] = acc[art.source] || []).push(art);
    return acc;
  }, {});
  const industry = filtered.filter((a) => a.category === 'industry');

  return (
    <div className="container">
      <h1>Analytics News</h1>
      <input
        type="text"
        placeholder="Search articles"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {Object.entries(vendorSections).map(([vendor, arts]) => (
        <Section key={vendor} title={vendor} articles={arts} />
      ))}
      <Section title="Industry" articles={industry} />
    </div>
  );
}

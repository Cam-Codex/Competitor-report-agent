import React from 'react';

export default function Section({ title, articles }) {
  if (!articles.length) return null;
  return (
    <section className="section">
      <h2>{title}</h2>
      {articles.map((art) => (
        <article key={art.link} className="card">
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

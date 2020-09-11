import React from 'react';
import { useState } from 'react';

import Header from './header';
import Search from './search';
import PreprintInfo from './preprint-info';
import SimilarJournals from './similar-journals';
import SimilarPapers from './similar-papers';
import MapSection from './map-section';
import About from './about';
import Footer from './footer';

import './app.css';

import { empty } from './status';

// main app component

export default () => {
  // data status
  const [status, setStatus] = useState(empty);

  // main data
  const [preprint, setPreprint] = useState('');
  const [similarJournals, setSimilarJournals] = useState([]);
  const [similarPapers, setSimilarPapers] = useState([]);
  const [coordinates, setCoordinates] = useState({});

  // render
  return (
    <>
      <Header />
      <main>
        <Search
          {...{
            preprint,
            setPreprint,
            status,
            setStatus,
            setSimilarJournals,
            setSimilarPapers,
            setCoordinates
          }}
        />
        <hr />
        {status !== empty && (
          <>
            <PreprintInfo {...{ preprint, status }} />
            <hr />
            <SimilarPapers {...{ similarPapers, status }} />
            <hr />
            <SimilarJournals {...{ similarJournals, status }} />
            <hr />
          </>
        )}
        <MapSection {...{ coordinates }} />
        <hr />
        <About />
      </main>
      <Footer />
    </>
  );
};

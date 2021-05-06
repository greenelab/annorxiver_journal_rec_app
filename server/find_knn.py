import numpy as np
import pandas as pd
import pickle
from sklearn.neighbors import KNeighborsClassifier
from document_downloader import get_doi_content
from find_coordinates import get_coordinates
from utils import get_journal_model, get_paper_model, get_pmc_map, server_log, timeout
from word_vectors import parse_content

N_NEIGHBORS = 10  # number of closest neighbors to find

# Build journal_model
journal_df, journal_model = get_journal_model(N_NEIGHBORS)

# Build paper_model
paper_model = get_paper_model(N_NEIGHBORS)

# Build paper PMC map
pmc_map = get_pmc_map()


@timeout(seconds=240)
def get_neighbors(user_doi):
    """
    Find the closest papers and journals given an input paper's DOI.
    Arguments:
        - user_doi: biorxiv DOI
    """

    server_log(f"Received user DOI ({user_doi})")

    content, paper_metadata, xml_found = get_doi_content(user_doi)
    server_log(f"Downloaded {'XML' if xml_found else 'PDF'} content of {user_doi}")
    query_vec = parse_content(content, xml_file=xml_found)

    server_log(f"Start searching {user_doi}")

    paper_knn = get_paper_knn(query_vec)
    journal_knn = get_journal_knn(query_vec)
    coordinates = get_coordinates(query_vec)
    server_log(f"Finished searching {user_doi}\n")

    return {
        "paper_neighbors": paper_knn,
        "journal_neighbors": journal_knn,
        "coordinates": coordinates,
        "paper_info": paper_metadata,
        "xml_found": xml_found
    }


def get_journal_knn(query_vec):
    """Find the K nearest journals."""

    A_journal = journal_model.kneighbors_graph(query_vec, mode="distance")
    matched_rows = list(A_journal.indices)
    journal_data = list(
        zip(
            A_journal.data,
            journal_df.reset_index().document[matched_rows].tolist(),
        )
    )

    journal_knn = [
        dict(
            distance=np.round(data_row[0], 3),
            document=data_row[1],
        )
        for data_row in journal_data
    ]

    return journal_knn


def get_paper_knn(query_vec):
    """Find the K nearest papers."""

    paper_knn = list()
    papers = paper_model.kneighbors_graph(query_vec, mode="distance")

    matched_rows = list(papers.indices)
    distances = list(papers.data)

    for idx, row in enumerate(matched_rows):
        node = {
            "distance": distances[idx],
            "pmcid": pmc_map[row],
        }
        paper_knn.append(node)

    return paper_knn

from io import BytesIO
import pickle

import lxml.etree as ET
import numpy as np
import spacy
import fitz

nlp = spacy.load("en_core_web_sm")
word_model_wv = pickle.load(open("data/word2vec_model/word_model.wv.pkl", "rb"))
filter_tag_list = [
    "sc",
    "italic",
    "xref",
    "label",
    "sub",
    "sup",
    "inline-formula",
    "fig",
    "disp-formula",
    "bold",
    "table-wrap",
    "table",
    "thead",
    "tbody",
    "caption",
    "tr",
    "td",
]
parser = ET.XMLParser(encoding="UTF-8", recover=True)


def parse_content(content, xml_file=True):
    """
    Parses input content and returns a vector based on the pre-loaded
    `word_model_wv`.
    Args:
        content - a PDF file's contents to be parsed
    """
    word_vectors = []
    if xml_file:
        biorxiv_xpath_str = (
            "//abstract/p|//abstract/title|//body/sec//p|//body/sec//title"
        )

        # Parse the xml document
        root = ET.fromstring(content, parser=parser)

        # Process xml without specified tags
        ET.strip_tags(root, *filter_tag_list)

        all_tags = root.xpath(biorxiv_xpath_str)
        text_to_process = list(map(lambda x: list(x.itertext()), list(all_tags)))

        for text in text_to_process:
            tokens = list(map(str, nlp(text[0])))

            word_vectors += [
                word_model_wv[tok]
                for tok in tokens
                if tok in word_model_wv and tok not in nlp.Defaults.stop_words
            ]
    else:

        # Have a faux file stream for parsing
        text_to_process = BytesIO(content)

        # Use this function to write pdf text to the file stream
        pdf_parser = fitz.open(stream=text_to_process, filetype="pdf")

        # Convert text to word vectors and continue processing
        for page in pdf_parser:
            tokens = list(map(str, nlp(page.getText())))

            word_vectors += [
                word_model_wv[tok]
                for tok in tokens
                if tok in word_model_wv and tok not in nlp.Defaults.stop_words
            ]

    word_embedd = np.stack(word_vectors)
    query_vec = word_embedd.mean(axis=0)[np.newaxis, :]
    return query_vec

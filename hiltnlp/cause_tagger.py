#!/usr/bin/env python3

import os
import argparse
import gatenlp
import hiltnlp
import Levenshtein

causal_words = [
    "because",
]

def is_causal_word(string):
    return any(
        Levenshtein.ratio(string, causal_word) > 0.9
        for causal_word in causal_words
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="(temp)"
    )
    parser.add_argument(
        "-i",
        "--annotation-file",
        dest="annotation_files",
        nargs="+",
        required="true",
        help="GATE annotation files"
    )
    args = parser.parse_args()

    for annotation_file_path in args.annotation_files:

        annotation_file = gatenlp.AnnotationFile(annotation_file_path)
        tokens = hiltnlp.get_tokens(annotation_file)

        causal_words_set = annotation_file.create_annotation_set("causal_words")

        for token in tokens:
            if is_causal_word(token.text):
                causal_words_set.create_annotation(
                    annotation_type="causal_word",
                    start=token.start_node,
                    end=token.end_node,
                )

        annotation_file.save_changes()

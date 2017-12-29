#!/usr/bin/env python3

import gatenlp
import collections


first_reference_words = [
    "i",
    "me",
    "my",
    "mine",
    "myself",
    "we",
    "us",
    "our",
    "ours",
    "ourselves",
]
second_reference_words = [
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
]
third_reference_words = [
    "he",
    "him",
    "himself",
    "his",
    "she",
    "her",
    "herself",
    "hers",
]

class Turn:
    def __init__(self,
                 sentences):
        self._sentences = sentences
        self._next = None
        self._previous = None
        self._speaker = get_speaker(self.sentences[0])

    def __str__(self):
        return "\n".join(sentence.text for sentence in self.sentences)

    def __repr__(self):
        sentences_string = str(self.sentences)
        return sentences_string

    def __iter__(self):
        for sentence in self.sentences:
            yield sentence

    def __getitem__(self, index):
        return self.sentences[index]

    def __setitem__(self, key, sentence):
        self.sentences[key] = sentence

    def append(self, sentence):
        self.sentences.append(sentence)

    @property
    def start_node(self):
        return self.sentences[0].start_node

    @property
    def end_node(self):
        return self.sentences[-1].end_node

    @property
    def speaker(self):
        return self._speaker

    @property
    def sentences(self):
        return self._sentences

    @property
    def next(self):
        return self._next

    @property
    def previous(self):
        return self._previous

    @next.setter
    def next(self, turn):
        if turn:
            if type(turn) != type(self):
                raise TypeError("'next' attribute must be same type")
        self._next = turn

    @previous.setter
    def previous(self, turn):
        if turn:
            if type(turn) != type(self):
                raise TypeError("'previous' attribute must be same type")
        self._previous = turn

def get_speaker(sentence):
    return sentence.features["Speaker"].value

def is_complete(sentence):
    pass
    return is_complete

def is_turn_head(sentence):
    return sentence.features["Turn_head"].value == "True"

def is_explicit_person_reference(token):
    return bool(
        token.text.lower() in (
            first_reference_words
            + second_reference_words
            + third_reference_words
        )
    )

def get_grammatical_person(person_token):
    if person_token.text.lower() in first_reference_words:
        return 1
    if person_token.text.lower() in second_reference_words:
        return 2
    if person_token.text.lower() in third_reference_words:
        return 3

def get_sentences(annotation_file):
    sentences = [
        annotation
        for annotation in annotation_file.annotations
        if annotation.type.lower() == "sentence"
    ]
    gatenlp.dlink(sentences)
    return sentences

def get_intersecting_of_type(annotation,
                             annotation_type):
    tree = annotation.annotation_file.interval_tree
    return [
        intersecting_annotation
        for intersecting_annotation in tree.search(annotation)
        if intersecting_annotation.type == annotation_type
    ]

def get_tokens(annotation):
    return get_intersecting_of_type(annotation, "Token")

def get_turns(sentences,
              overwrite=False):
    sentences = sorted(
        sentences,
        key=lambda x: x.start_node,
    )
    tag_speakers(sentences)
    tag_turns(sentences)
    sentence_queue = collections.deque(sentences)

    turns = []
    turn_sentences = []
    while sentence_queue:
        current_sentence = sentence_queue.popleft()
        if is_turn_head(current_sentence):
            turns.append(Turn(turn_sentences))
            turn_sentences = []
            turn_sentences.append(current_sentence)
        else:
            turn_sentences.append(current_sentence)
    if turn_sentences:
        turns.append(Turn(turn_sentences))

    gatenlp.dlink(turns)

    # for turn in turns:
        # if not is_complete(turn[-1]):

    # assign turns to sentences
    for turn in turns:
        for sentence in turn:
            sentence.turn = turn

    return turns

def tag_turns(sentences,
              overwrite=False):
    """Will add a feature to each sentence's XML with a Name of
    'Turn_head' with a Value of either 'True' or 'False'
    """

    sentences = sorted(
        sentences,
        key=lambda x: x.start_node
    )

    for sentence in sentences:
        if get_speaker(sentence) == "None":
            sentence.add_feature("Turn_head", "False", overwrite=overwrite)
            continue

        if not sentence.previous:
            sentence.add_feature("Turn_head", "True", overwrite=overwrite)
            continue
        if not sentence.previous.previous:
            sentence.add_feature("Turn_head", "True", overwrite=overwrite)
            continue

        previous_speaker = get_speaker(sentence.previous)
        current_speaker = get_speaker(sentence)

        if previous_speaker == current_speaker:
            sentence.add_feature("Turn_head", "False", overwrite=overwrite)
        else:
            if previous_speaker == "None":
                if get_speaker(sentence.previous.previous) == current_speaker:
                    sentence.add_feature("Turn_head", "False", overwrite=overwrite)
                else:
                    sentence.add_feature("Turn_head", "True", overwrite=overwrite)
            else:
                sentence.add_feature("Turn_head", "True", overwrite=overwrite)

def tag_speakers(sentences,
                 overwrite=False):
    """Will add a feature to each sentence's XML with a Name of
    'Speaker' and a Value of  the speaker tag for the current turn
    """

    assert all(
        type(sentence) == gatenlp.Annotation
        for sentence in sentences
    )

    media_file_extensions = [
        ".mp3",
        ".mp4",
        ".aiff",
        ".raw",
        ".wav",
        ".flac",
    ]

    sentences = sorted(
        sentences,
        key=lambda x: x.start_node
    )

    speaker_tag = "None"
    for sentence in sentences:
        text = sentence.text
        if any(
            file_extension in text.lower()
            for file_extension in media_file_extensions
        ):
            sentence.add_feature("Speaker", "None", overwrite=overwrite)
            continue
        if ":" in text:
            speaker_tag = text.split(":")[0]
        sentence.add_feature("Speaker", speaker_tag, overwrite=overwrite)

def test():
    print("all good")

if __name__ == "__main__":

    conversations_dir = "/home/nick/hilt/pes/conversations"

    annotation_file_paths = [
        os.path.join(root, f)
        for root, dirs, files in os.walk(conversations_dir)
        for f in files
        if f.lower().endswith("pes_3_consensus.xml")
    ]

    sentence_terminals = set()
    for annotation_file_path in annotation_file_paths:

        annotation_file = gatenlp.AnnotationFile(annotation_file_path)
        annotations = annotation_file.annotations
        sentences = (
            annotation
            for annotation in annotations
            if annotation.type.lower() == "sentence"
        )
        sentences = sorted(
            sentences, key=lambda x: x.start_node
        )
        gatenlp.dlink(sentences)

        for sentence in sentences:
            if len(sentence) == 3:
                sentence_terminals.add(sentence.text)
        # print(is_complete(sentence))

        ## prints each turn in the doc
        # for sentence in sentences:
            # print(
                # get_speaker(sentence)[0],
                # str(is_turn_head(sentence)).upper().rjust(5,"."),
            # )

        continue
        # annotation_file.save_changes()
    print(sentence_terminals)

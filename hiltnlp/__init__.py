#!/usr/bin/env python3
"""
This package provides further abstraction on top of :mod:`gatenlphiltlab`, tailored to
the needs of `the HiLT Lab at the University of North Texas
<http://hilt.cse.unt.edu/>`_.
"""

import gatenlphiltlab
import collections


#: All of the words considered explicit to be first person references
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

#: All of the words considered explicit to be second person references
second_reference_words = [
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
]

#: All of the words considered explicit to be third person references
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
    """
    Abstraction of a linguistic `turn <https://glossary.sil.org/term/turn>`_
    within a GATE annotation file of a HiLT transcript. More information about
    how turns are notated can be found in the HiLT Transcription Guidelines.

    :param sentences: The sentences of the conversation to be parsed into turns. The sentences must be :func:`doubly linked <gatenlphiltlab.dlink>`.
    :type sentences: list(:class:`gatenlphiltlab.Annotation`)
    """
    def __init__(self,
                 sentences):
        self._sentences = sentences
        self._next = None
        self._previous = None
        self._speaker = get_speaker(self.sentences[0])

    def __str__(self):
        return "\n".join(
            sentence.text
            for sentence in self.sentences
        )

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
        """
        Appends a sentence to this turn.

        :param sentence: The sentence to append
        :type sentence: :class:`gatenlphiltlab.Annotation`
        """
        self.sentences.append(sentence)

    @property
    def start_node(self):
        """
        The offset corresponding to the beginning of this turn in the
        annotation file's text.

        :type: int
        """
        return self.sentences[0].start_node

    @property
    def end_node(self):
        """
        The offset corresponding to the end of this turn in the annotation
        file's text.
        
        :type: int
        """
        return self.sentences[-1].end_node

    @property
    def speaker(self):
        """
        The speaker of this turn.

        :type: string
        """
        return self._speaker

    @property
    def sentences(self):
        """
        The sentences that comprise this turn.

        :type: list(:class:`gatenlphiltlab.Annotation`)
        """
        return self._sentences

    @property
    def next(self):
        """
        The next turn in the conversation.

        :type: :class:`~hiltnlp.Turn`
        """
        return self._next

    @property
    def previous(self):
        """
        The previous turn in the conversation.

        :type: :class:`~hiltnlp.Turn`
        """
        return self._previous

    @next.setter
    def next(self, turn):
        if turn:
            if type(turn) != type(self):
                raise TypeError(
                    "'next' attribute must be same type"
                )
        self._next = turn

    @previous.setter
    def previous(self, turn):
        if turn:
            if type(turn) != type(self):
                raise TypeError(
                    "'previous' attribute must be same type"
                )
        self._previous = turn

def get_speaker(sentence):
    return sentence.features["Speaker"].value

# TODO: complete is_complete
def is_complete(sentence):
    """
    This function is currently incomplete (Ironic, huh?). Intended to determine
    if the given *sentence* is grammatically complete.

    :param sentence: The sentence.
    :type sentence: :class:`gatenlphiltlab.Annotation`
    :rtype: bool
    """
    pass

def is_turn_head(sentence):
    """
    Returns *True* if *sentence* begins a new turn. *sentence* must have a
    feature called "Turn_head" with a string value of either "True" or "False".

    :param sentence: The sentence.
    :type sentence: :class:`gatenlphiltlab.Annotation`
    :rtype: bool
    """
    return sentence.features["Turn_head"].value == "True"

def is_explicit_person_reference(token):
    """
    Returns *True* if the string of *token* is in
    :data:`~hiltnlp.first_reference_words`,
    :data:`~hiltnlp.second_reference_words`, or
    :data:`~hiltnlp.third_reference_words`.

    :param token: The token.
    :type token: :class:`gatenlphiltlab.Annotation`
    :rtype: bool
    """
    return bool(
        token.text.lower() in (
            first_reference_words
            + second_reference_words
            + third_reference_words
        )
    )

def get_grammatical_person(person_token):
    """
    Retrieves the `grammatical person
    <https://en.wikipedia.org/wiki/Grammatical_person>`_ of *person_token*,
    limited to either first, second, or third person. Currently limited to the
    obvious pronouns listed in :data:`~hiltnlp.first_reference_words`,
    :data:`~hiltnlp.second_reference_words`, and
    :data:`~hiltnlp.third_reference_words`.

    :param token: The token.
    :type token: :class:`gatenlphiltlab.Annotation`

    :returns: The grammatical person of *person_token*.
    :rtype: int
    """
    if person_token.text.lower() in first_reference_words:
        return 1
    if person_token.text.lower() in second_reference_words:
        return 2
    if person_token.text.lower() in third_reference_words:
        return 3

def get_sentences(annotation_file):
    """
    Given a :class:`GATE annotation file <gatenlphiltlab.AnnotationFile>`, return its
    contained sentences.

    :param annotation_file: The annotation file.
    :type annotation_file: :class:`gatenlphiltlab.AnnotationFile`

    :returns: The sentences contained within *annotation_file*, :func:`doubly-linked <gatenlphiltlab.dlink>`.
    :rtype: list(:class:`gatenlphiltlab.Annotation`)
    """
    sentences = [
        annotation
        for annotation in annotation_file.annotations
        if annotation.type.lower() == "sentence"
    ]
    gatenlphiltlab.dlink(sentences)
    return sentences

def get_near_sentences(sentence,
                       distance=1,
                       before=True,
                       after=True):
    """
    Given *sentence*, return its surrounding sentences.

    :returns: The nearby sentences.
    :rtype: list(:class:`gatenlphiltlab.Annotation`)

    :param sentence: The origin sentence.
    :type sentence: :class:`gatenlphiltlab.Annotation`

    :param distance: How far to collect sentences in terms of sentences.
    :type distance: int

    :param before: Seek before *sentence*.
    :type before: bool

    :param after: Seek after *sentence*.
    :type after: bool
    """
    if not (before or after):
        return

    desired_distance = distance

    before_sentences = []
    current_distance = 0
    current_sentence = sentence
    while current_distance < desired_distance:
        previous_sentence = current_sentence.previous
        if not previous_sentence:
            break
        before_sentences.append(previous_sentence)
        current_distance += 1
        current_sentence = previous_sentence

    after_sentences = []
    current_distance = 0
    current_sentence = sentence
    while current_distance < desired_distance:
        next_sentence = current_sentence.next
        if not next_sentence:
            break
        after_sentences.append(next_sentence)
        current_distance += 1
        current_sentence = next_sentence

    near_sentences = []
    if before:
        for x in before_sentences:
            near_sentences.append(x)
    if after:
        for x in after_sentences:
            near_sentences.append(x)

    return near_sentences

def get_tokens(annotation_or_annotation_file):
    if type(annotation_or_annotation_file) == gatenlphiltlab.AnnotationFile:
        annotation_file = annotation_or_annotation_file
        return [
            annotation
            for annotation in annotation_file.annotations
            if annotation.type == "Token"
        ]
    if type(annotation_or_annotation_file) == gatenlphiltlab.Annotation:
        annotation = annotation_or_annotation_file
        return annotation.get_intersecting_of_type("Token")

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

    gatenlphiltlab.dlink(turns)

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
            sentence.add_feature(
                "Turn_head",
                "False",
                overwrite=overwrite,
            )
            continue

        if not sentence.previous:
            sentence.add_feature(
                "Turn_head",
                "True",
                overwrite=overwrite,
            )
            continue
        if not sentence.previous.previous:
            sentence.add_feature(
                "Turn_head",
                "True",
                overwrite=overwrite,
            )
            continue

        previous_speaker = get_speaker(sentence.previous)
        current_speaker = get_speaker(sentence)

        if previous_speaker == current_speaker:
            sentence.add_feature(
                "Turn_head",
                "False",
                overwrite=overwrite,
            )
        else:
            if previous_speaker == "None":
                if get_speaker(sentence.previous.previous) == current_speaker:
                    sentence.add_feature(
                        "Turn_head",
                        "False",
                        overwrite=overwrite,
                    )
                else:
                    sentence.add_feature(
                        "Turn_head",
                        "True",
                        overwrite=overwrite,
                    )
            else:
                sentence.add_feature(
                    "Turn_head",
                    "True",
                    overwrite=overwrite,
                )

def tag_speakers(sentences,
                 overwrite=False):
    """Will add a feature to each sentence's XML with a Name of
    'Speaker' and a Value of  the speaker tag for the current turn
    """

    assert all(
        type(sentence) == gatenlphiltlab.Annotation
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

        annotation_file = gatenlphiltlab.AnnotationFile(annotation_file_path)
        annotations = annotation_file.annotations
        sentences = (
            annotation
            for annotation in annotations
            if annotation.type.lower() == "sentence"
        )
        sentences = sorted(
            sentences, key=lambda x: x.start_node
        )
        gatenlphiltlab.dlink(sentences)

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

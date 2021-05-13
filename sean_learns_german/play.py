import functools
import random
import typing

import genanki
import panwid.keymap
from panwid.dropdown import *
from panwid.listbox import *
from panwid.keymap import *
import urwid
import urwid.raw_display
import urwid.widget
from urwid_utils.palette import *

from sean_learns_german.notion_client import GermanBankNotionClient
from sean_learns_german.words import BANK_NOUNS, BANK_VERBS
from sean_learns_german.models.basic_sentence import BasicSentence


def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


panwid.keymap.KEYMAP_GLOBAL = {
    "movement": {
        "up": "up",
        "down": "down",
    },
    "dropdown": {
        "k": "up",
        "j": "down",
        "page up": "page up",
        "page down": "page down",
        "ctrl up": ("cycle", [1]),
        "ctrl down": ("cycle", [-1]),
        "home": "home",
        "end": "end",
        "/": "complete prefix",
        "?": "complete substring",
        "ctrl p": "complete_prev",
        "ctrl n": "complete_next",
    },
    "auto_complete_edit": {
        "enter": "confirm",
        "esc": "cancel",
        "/": "complete prefix",
        "?": "complete substring",
        "ctrl p": "complete_prev",
        "ctrl n": "complete_next",
    }
}


class TestDropdown(KeymapMovementMixin, Dropdown):
    pass



def main():
    notion_client = GermanBankNotionClient('411a63435bf2da100d421adbd47a5a40548a5497feb1b5b1bb1c21935d0a83e8288fadf1a43c4c426e930399c65f2eafc057d089da1f5556580511c717d034deb0070423b3e5e4c5e442dd1255a3')
    bank_nouns = sorted([noun for noun in notion_client.get_bank_nouns()])
    bank_verbs = sorted([verb for verb in notion_client.get_bank_verbs()])

    # bank_nouns = sorted(BANK_NOUNS)
    # bank_verbs = sorted(BANK_VERBS)

    nouns = [noun.german_word_singular for noun in bank_nouns]
    verbs = [verb.german_word for verb in bank_verbs]

    entries = Dropdown.get_palette_entries()
    entries.update(ScrollingListBox.get_palette_entries())
    palette = Palette("default", **entries)
    screen = urwid.raw_display.Screen()
    screen.set_terminal_properties(256)

    subject = TestDropdown(
        items=nouns,
        # label="nouns",
        scrollbar=True,
        auto_complete=True,
        left_chars=' ',
        right_chars=' ',
    )

    verb = TestDropdown(
        items=verbs,
        # label="verbs",
        scrollbar=True,
        auto_complete=True,
        left_chars=' ',
        right_chars=' ',
    )

    object_ = TestDropdown(
        items=nouns,
        # label="nouns",
        scrollbar=True,
        auto_complete=True,
        left_chars=' ',
        right_chars=' ',
    )

    boxes = [subject, verb, object_]
    boxes_grid = urwid.Columns(boxes)
    blank_it = {"blanked": "verb"}  # Lazy hack to make this accessible within sub method

    def add_sentence_to_deck(basic_sentence: BasicSentence, _):
        deck.add_note(basic_sentence.to_anki_note())

    def generate_all_sentences_as_buttons() -> typing.List[urwid.Button]:
        return [
            urwid.Button(
                label=f"{basic_sentence.get_question_sentence(blank_it['blanked'])} | {basic_sentence.get_answer_sentence()}",
                on_press=functools.partial(add_sentence_to_deck, basic_sentence),
            )
            for basic_sentence in generate_all_sentences()
        ]

    def generate_all_sentences() -> typing.List[BasicSentence]:
        subject2 = bank_nouns[subject.selected_value].random_noun().first()
        verb2 = bank_verbs[verb.selected_value]
        object2 = bank_nouns[object_.selected_value].random_noun().first()
        res = []

        while True:
            basic_sentence = BasicSentence(subject2, verb2, object2)
            res.append(basic_sentence)
            
            try:
                try:
                    subject2 = subject2.rotate()
                except StopIteration:
                    subject2 = subject2.first()
                    object2 = object2.rotate()
            except StopIteration:
                break
        
        return res

    deck = genanki.Deck(
        deck_id=1878326705,  # Hard-coded value selected by me
        name="German::Grammar",
    )

    sentence_list = urwid.Pile(generate_all_sentences_as_buttons())

    def refresh_all_sentences(_, __):
        sentence_list.widget_list = generate_all_sentences_as_buttons()

    urwid.connect_signal(subject.pop_up, "select", refresh_all_sentences)
    urwid.connect_signal(verb.pop_up, "select", refresh_all_sentences)
    urwid.connect_signal(object_.pop_up, "select", refresh_all_sentences)

    pile = urwid.Pile([boxes_grid, sentence_list])
    main = urwid.Frame(urwid.Filler(pile, valign=urwid.widget.TOP))

    def global_input(key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key == 'R':
            for box in boxes:
                box.select_value(random.randint(0, len(box.values)-1))

            refresh_all_sentences(None, None)
        elif key == 'r':
            try:
                focused_box = main.get_focus_widgets()[-2]
            except IndexError:
                pass

            if focused_box in boxes:
                focused_box.select_value(random.randint(0, len(focused_box.values)-1))

            refresh_all_sentences(None, None)
        elif key in ('b', 'B'):
            try:
                focused_box = main.get_focus_widgets()[-2]
            except IndexError:
                pass
            else:
                if focused_box == subject:
                    blank_it["blanked"] = "subject"
                elif focused_box == verb:
                    blank_it["blanked"] = "verb"
                elif focused_box == object_:
                    blank_it["blanked"] = "object"

            refresh_all_sentences(None, None)
        else:
            return False

    loop = urwid.MainLoop(
        main,
        palette,
        screen=screen,
        unhandled_input=global_input,
        pop_ups=True,
    )

    loop.run()

    if deck.notes:
        genanki.Package([deck]).write_to_file("play.apkg")
        print(f"Complete! Added {len(deck.notes)} cards. Now import play.apkg to Anki, fix any changes, and sync Anki to AnkiCloud.")


if __name__ == '__main__':
    main()

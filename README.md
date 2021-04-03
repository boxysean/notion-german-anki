## notion-german-anki

### Project requirements

This project is to allow my Notion German bank to be my "source of truth" for my Anki dictionary. It has the following aims:

- Easily extract Notion table to create Anki notes / cards, with specific tags for my ease-of-use.
- Retain the Anki stats if I make any updates.
- Generate grammar cards that can easily be imported

### How to run

1. Install python requirements with `pipenv install`
2. Run `python -m sean_learns_german.cli generate-decks --token xyz` to generate a deck called `output.apkg`
3. Import `output.apkg` into Anki on computer
4. Sync Anki to main database

### Roadmap

- [ ] Deal with German synonyms (each card must be a one-to-N answer). I would need to collect all the entries and make synonyms.
- [ ] Add sentences to deck, if they exist.
- [x] Add part of speech demarcation to cards.
- [x] Add conjugation for verbs.
- [ ] Add normative and accusative case example sentences.

import dataclasses
import typing

import click
import genanki
import notion.client
import notion.collection


@dataclasses.dataclass
class GermanBankItem:
    gender: typing.Optional[str]
    german: str
    english: str
    part_of_speech: str
    tags: typing.List[str]

    @classmethod
    def from_notion_row(cls, row: notion.collection.CollectionRowBlock) -> "GermanBankItem":
        return GermanBankItem(
            gender=row.gender,
            german=row.german,
            english=row.english,
            part_of_speech=row.part_of_speech,
            tags=row.tags,
        )


class GermanNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0], self.fields[1])


@click.command()
@click.option("--token", type=str, help="Get from token_v2 value stored in www.notion.so cookies. Link: chrome://settings/cookies/detail?site=www.notion.so", required=True,)
def main(token: str) -> None:
    client = notion.client.NotionClient(token_v2=token)
    view = client.get_collection_view("https://www.notion.so/0bf4b6fd23af40dba8d4c23206b2f1e3?v=e2f51d7caf4a43c7a791304984f019bb")

    model = genanki.Model(
        model_id=1522879452,  # hard coded
        name="Generated German",
        fields=[
            {"name": "German"},
            {"name": "English"},
        ],
        templates=[
            {
                "name": "English -> German",
                "qfmt": "{{English}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{German}}',
            },
            {
                "name": "German -> English",
                "qfmt": "{{German}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{English}}',
            },
        ],
        css=""".card {
 font-family: arial;
 font-size: 20px;
 text-align: center;
 color: black;
 background-color: white;
}"""
    )

    deck = genanki.Deck(
        deck_id=1772660115,
        name="German (Generated)",
    )

    for row in view.collection.get_rows():
        german_bank_item = GermanBankItem.from_notion_row(row)

        note = genanki.Note(
            model=model,
            fields=[
                german_bank_item.german,
                german_bank_item.english,
            ],
            tags=[german_bank_item.part_of_speech] if german_bank_item.part_of_speech else [] + german_bank_item.tags,
        )

        deck.add_note(note)

    genanki.Package(deck).write_to_file('output.apkg')


if __name__ == "__main__":
    main()

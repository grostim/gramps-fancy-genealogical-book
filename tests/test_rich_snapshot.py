import json
from types import SimpleNamespace

from gramps_fancy_book.gramps_adapter import GrampsDatabaseAdapter
from gramps_fancy_book.normalization import build_book_model


def obj(**methods):
    return SimpleNamespace(
        **{
            name: value if callable(value) else (lambda value=value: value)
            for name, value in methods.items()
        }
    )


def event_ref(handle, role=""):
    return SimpleNamespace(
        ref=handle,
        get_role=lambda: SimpleNamespace(string=role),
        get_citation_list=lambda: ["citation-1"],
        get_note_list=lambda: [],
        get_attribute_list=lambda: [],
        get_privacy=lambda: False,
    )


def media_ref(handle, rectangle=None):
    return SimpleNamespace(
        ref=handle,
        get_rectangle=lambda: rectangle,
        get_privacy=lambda: False,
        get_citation_list=lambda: [],
        get_note_list=lambda: [],
        get_attribute_list=lambda: [],
    )


class StyledText:
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

    def get_tags(self):
        return []


class Database:
    def __init__(self, records):
        self.records = records
        self.reads = {}

    def __getattr__(self, name):
        prefix = "get_"
        suffix = "_from_handle"
        if name.startswith(prefix) and name.endswith(suffix):
            kind = name[len(prefix) : -len(suffix)]

            def get(handle):
                key = kind, handle
                self.reads[key] = self.reads.get(key, 0) + 1
                return self.records.get(kind, {}).get(handle)

            return get
        raise AttributeError(name)


def rich_database():
    tags = {
        "tag-publication": obj(get_handle="tag-publication", get_name="BOOK_PUBLICATION"),
        "tag-working": obj(get_handle="tag-working", get_name="WORKING"),
        "tag-featured": obj(get_handle="tag-featured", get_name="BOOK_FEATURED"),
        "tag-exclude": obj(get_handle="tag-exclude", get_name="BOOK_EXCLUDE"),
    }
    person0 = obj(
        get_handle="person-0",
        get_gramps_id="I0001",
        get_primary_name=lambda: obj(get_name="Ada Exemple"),
        get_alternate_names=lambda: [obj(get_name="Ada née Martin")],
        get_gender=2,
        get_family_handle_list=lambda: ["family-main", "family-union"],
        get_parent_family_handle_list=lambda: ["family-parents"],
        get_event_ref_list=lambda: [event_ref("event-life", "Primary")],
        get_citation_list=lambda: [],
        get_note_list=lambda: [],
        get_tag_list=lambda: [],
        get_attribute_list=lambda: [obj(get_type=lambda: SimpleNamespace(string="BOOK_PROFILE"), get_value="YES")],
        get_media_list=lambda: [media_ref("media-featured", (10, 20, 80, 90))],
        get_privacy=lambda: True,
        get_person_ref_list=lambda: [SimpleNamespace(
            ref="person-godparent", rel="Godparent", get_citation_list=lambda: [],
            get_note_list=lambda: [], get_privacy=lambda: True,
        )],
        get_address_list=lambda: [obj(
            get_street="10 rue des Lilas", get_locality="Vieux Lyon", get_city="Lyon",
            get_county="Rhône", get_state="Auvergne-Rhône-Alpes", get_country="France",
            get_postal_code="69001", get_phone="01 02 03 04 05",
            get_date_object=lambda: None, get_citation_list=lambda: ["citation-1"],
            get_note_list=lambda: ["note-public"], get_privacy=lambda: True,
        )],
        get_url_list=lambda: [SimpleNamespace(
            get_path=lambda: "https://example.test/ada", get_description=lambda: "Notice",
            get_type=lambda: SimpleNamespace(string="Web Home"),
        )],
    )
    person1 = obj(
        get_handle="person-1", get_gramps_id="I0002",
        get_primary_name=lambda: obj(get_name="Basile Exemple"),
        get_alternate_names=lambda: [], get_gender=1,
        get_family_handle_list=lambda: ["family-main"],
        get_parent_family_handle_list=lambda: [],
        get_event_ref_list=lambda: [], get_citation_list=lambda: [], get_note_list=lambda: [],
        get_tag_list=lambda: [], get_attribute_list=lambda: [], get_media_list=lambda: [],
        get_privacy=lambda: False,
    )
    person2 = obj(
        get_handle="person-2", get_gramps_id="I0003",
        get_primary_name=lambda: obj(get_name="Camille Exemple"),
        get_alternate_names=lambda: [], get_gender=0,
        get_family_handle_list=lambda: [], get_parent_family_handle_list=lambda: ["family-main"],
        get_event_ref_list=lambda: [], get_citation_list=lambda: [], get_note_list=lambda: [],
        get_tag_list=lambda: [], get_attribute_list=lambda: [], get_media_list=lambda: [],
        get_privacy=lambda: False,
    )
    persons = {"person-0": person0, "person-1": person1, "person-2": person2}

    def family(handle, father, mother, children):
        return obj(
            get_handle=handle, get_gramps_id=handle.upper(),
            get_father_handle=father, get_mother_handle=mother,
            get_child_ref_list=lambda: children,
            get_relationship=lambda: SimpleNamespace(string="Married"),
            get_event_ref_list=lambda: [event_ref("event-union", "Family")] if handle == "family-main" else [],
            get_citation_list=lambda: [], get_note_list=lambda: [], get_tag_list=lambda: [],
            get_attribute_list=lambda: [], get_media_list=lambda: [], get_privacy=lambda: False,
        )

    families = {
        "family-main": family("family-main", "person-0", "person-1", [
            SimpleNamespace(
                ref="person-2",
                get_father_relation=lambda: SimpleNamespace(string="Birth"),
                get_mother_relation=lambda: SimpleNamespace(string="Adopted"),
                get_citation_list=lambda: ["citation-1"],
                get_note_list=lambda: ["note-public"],
                get_privacy=lambda: True,
            ),
            SimpleNamespace(
                ref="person-none-parent",
                get_father_relation=lambda: SimpleNamespace(string="None"),
                get_mother_relation=lambda: SimpleNamespace(string="Birth"),
                get_citation_list=lambda: [],
                get_note_list=lambda: [],
                get_privacy=lambda: False,
            ),
        ]),
        "family-union": family("family-union", "person-0", None, []),
        "family-parents": family("family-parents", "person-3", "person-4", [
            SimpleNamespace(ref="person-0", get_father_relation=lambda: 0, get_mother_relation=lambda: 0)
        ]),
    }
    persons.update({
        handle: obj(
            get_handle=handle, get_gramps_id=handle.upper(),
            get_primary_name=lambda handle=handle: obj(get_name=handle), get_alternate_names=lambda: [],
            get_gender=0, get_family_handle_list=lambda: [], get_parent_family_handle_list=lambda: [],
            get_event_ref_list=lambda: [], get_citation_list=lambda: [], get_note_list=lambda: [],
            get_tag_list=lambda: [], get_attribute_list=lambda: [], get_media_list=lambda: [],
            get_privacy=lambda: False,
        )
        for handle in ("person-3", "person-4", "person-godparent", "person-none-parent")
    })

    date = obj(
        get_date_object=lambda: obj(
            get_text=lambda: "",
            get_sort_value=lambda: 2451545,
            get_modifier=lambda: 3,
            get_quality=lambda: 1,
            get_calendar=lambda: 0,
            get_ymd=lambda: (1900, 1, 1),
            get_stop_ymd=lambda: (1900, 1, 31),
            get_start_stop_range=lambda: ((1900, 1, 1), (1900, 1, 31)),
            serialize=lambda: (0, 1900, 1, 1, 0, 1900, 1, 31, 3, 1, ""),
        )
    )
    event_life = obj(
        get_handle="event-life", get_gramps_id="E0001",
        get_type=lambda: SimpleNamespace(string="Occupation"), get_description="Artisane",
        get_place_handle="place-1", **{
            "get_date_object": date.get_date_object,
            "get_citation_list": lambda: ["citation-1"],
            "get_note_list": lambda: ["note-public", "note-working"],
            "get_tag_list": lambda: [], "get_attribute_list": lambda: [],
            "get_media_list": lambda: [], "get_privacy": lambda: False,
        },
    )
    event_union = obj(
        get_handle="event-union", get_gramps_id="E0002",
        get_type=lambda: SimpleNamespace(string="Marriage"), get_description="",
        get_date_object=lambda: None, get_place_handle=lambda: None,
        get_citation_list=lambda: [], get_note_list=lambda: [], get_tag_list=lambda: [],
        get_attribute_list=lambda: [], get_media_list=lambda: [], get_privacy=lambda: False,
    )
    notes = {
        "note-public": obj(
            get_handle="note-public", get_gramps_id="N0001",
            get_tag_list=lambda: ["tag-publication"], get_styledtext=lambda: StyledText("Texte publiable"),
            get_format=lambda: 0, get_type=lambda: "General", get_citation_list=lambda: [],
            get_note_list=lambda: [], get_attribute_list=lambda: [], get_media_list=lambda: [],
            get_privacy=lambda: True,
        ),
        "note-working": obj(
            get_handle="note-working", get_gramps_id="N0002",
            get_tag_list=lambda: ["tag-working"], get_styledtext=lambda: StyledText("Texte interne"),
            get_format=lambda: 0, get_type=lambda: "General", get_citation_list=lambda: [],
            get_note_list=lambda: [], get_attribute_list=lambda: [], get_media_list=lambda: [],
            get_privacy=lambda: False,
        ),
    }
    media = obj(
        get_handle="media-featured", get_gramps_id="M0001", get_path="photos/a.jpg",
        get_description="Portrait", get_mime_type="image/jpeg", get_checksum="abc",
        get_tag_list=lambda: ["tag-featured", "tag-exclude"], get_citation_list=lambda: [],
        get_note_list=lambda: [], get_attribute_list=lambda: [], get_media_list=lambda: [],
        get_privacy=lambda: True,
    )
    citation = obj(
        get_handle="citation-1", get_gramps_id="C0001", get_reference_handle="source-1",
        get_page="p. 7", get_date_object=lambda: None, get_confidence_level=lambda: 2,
        get_url_list=lambda: [], get_citation_list=lambda: [], get_note_list=lambda: [],
        get_tag_list=lambda: [], get_attribute_list=lambda: [], get_media_list=lambda: [],
        get_privacy=lambda: False,
    )
    source = obj(
        get_handle="source-1", get_gramps_id="S0001", get_title="Registre paroissial",
        get_author="Archives", get_publication_info="1900", get_abbreviation="RP",
        get_reporef_list=lambda: [SimpleNamespace(
            ref="repository-1", get_call_number=lambda: "3 E 12", get_media_type=lambda: "Microfilm"
        )],
        get_url_list=lambda: [], get_citation_list=lambda: [], get_note_list=lambda: [],
        get_tag_list=lambda: [], get_attribute_list=lambda: [], get_media_list=lambda: [],
        get_privacy=lambda: False,
    )
    repository = obj(
        get_handle="repository-1", get_gramps_id="R0001", get_name="Archives municipales",
        get_type=lambda: SimpleNamespace(string="Library"), get_url_list=lambda: [],
        get_citation_list=lambda: [], get_note_list=lambda: [], get_tag_list=lambda: [],
        get_attribute_list=lambda: [], get_media_list=lambda: [], get_privacy=lambda: False,
    )
    place = obj(
        get_handle="place-1", get_gramps_id="P0001",
        get_name=lambda: obj(get_value="Lyon"), get_title="Lyon, Rhône",
        get_citation_list=lambda: [], get_note_list=lambda: [], get_tag_list=lambda: [],
        get_attribute_list=lambda: [], get_media_list=lambda: [], get_privacy=lambda: False,
    )
    return Database({
        "family": families,
        "person": persons,
        "event": {"event-life": event_life, "event-union": event_union},
        "place": {"place-1": place}, "note": notes, "citation": {"citation-1": citation},
        "source": {"source-1": source}, "repository": {"repository-1": repository},
        "media": {"media-featured": media}, "tag": tags,
    })


def test_snapshot_preserves_relationships_events_sources_media_and_privacy():
    db = rich_database()
    model = build_book_model(GrampsDatabaseAdapter(db).read_snapshot("family-main"))
    payload = model.to_dict()
    people = {person.handle: person for person in model.people}

    assert model.metadata["BOOK_SCHEMA_VERSION"] == "0.7"
    assert payload["privacy"]["contains_private_data"] is True
    assert payload["reference_family"]["child_relationships"] == [
        {
            "person_handle": "person-2", "father_relation": "Birth", "mother_relation": "Adopted",
            "order": 0, "citations": ["citation-1"], "notes": ["note-public"], "private": True,
        },
        {
            "person_handle": "person-none-parent", "father_relation": "None", "mother_relation": "Birth",
            "order": 1, "citations": [], "notes": [], "private": False,
        },
    ]
    assert set(payload["families"]) == {"family-main", "family-parents", "family-union"}
    assert model.events["event-life"].date.modifier == 3
    assert model.events["event-life"].date.ymd == (1900, 1, 1)
    assert model.events["event-life"].date.range == ((1900, 1, 1), (1900, 1, 31))
    assert isinstance(model.events["event-life"].date.raw, tuple)
    assert model.events["event-life"].links.events == ()
    assert people["person-0"].links.events[0].role == "Primary"
    assert people["person-0"].links.events[0].citations == ("citation-1",)
    assert people["person-0"].relationships[0].relation == "Godparent"
    assert people["person-0"].relationships[0].private is True
    assert people["person-godparent"].name == "person-godparent"
    assert people["person-0"].addresses[0].street == "10 rue des Lilas"
    assert people["person-0"].addresses[0].date is None
    assert people["person-0"].addresses[0].private is True
    assert people["person-0"].urls[0].path == "https://example.test/ada"
    assert model.places["place-1"].name == "Lyon"
    assert model.notes["note-public"].text == "Texte publiable"
    assert model.notes["note-public"].links.private is True
    assert model.notes["note-working"].is_publishable is False
    assert model.notes["note-working"].text is None
    assert model.citations["citation-1"].source_handle == "source-1"
    assert model.sources["source-1"].repository_refs[0].repository_handle == "repository-1"
    assert model.repositories["repository-1"].name == "Archives municipales"
    assert model.media["media-featured"].path == "photos/a.jpg"
    assert model.media["media-featured"].is_featured is True
    assert model.media["media-featured"].is_excluded is True
    assert people["person-0"].links.media[0].rectangle == (10, 20, 80, 90)
    assert people["person-0"].links.private is True
    assert people["person-0"].book_profile_forced is True
    assert db.reads[("citation", "citation-1")] == 1
    assert db.reads[("event", "event-life")] == 1
    assert json.loads(json.dumps(payload, ensure_ascii=False))["sources"]["source-1"]["title"] == "Registre paroissial"


def test_missing_optional_references_become_structured_diagnostics():
    db = rich_database()
    event = db.records["event"]["event-life"]
    event.get_citation_list = lambda: ["missing-citation"]

    model = build_book_model(GrampsDatabaseAdapter(db).read_snapshot("family-main"))

    assert any(
        item.code == "missing_reference"
        and item.object_type == "citation"
        and item.handle == "missing-citation"
        for item in model.diagnostics
    )


def test_invalid_book_profile_value_is_preserved_and_diagnosed():
    db = rich_database()
    person = db.records["person"]["person-0"]
    attributes = person.get_attribute_list()
    attributes[0].get_value = lambda: "true"
    person.get_attribute_list = lambda: attributes

    model = build_book_model(GrampsDatabaseAdapter(db).read_snapshot("family-main"))
    focal_person = next(person for person in model.people if person.handle == "person-0")

    assert focal_person.book_profile_forced is False
    assert focal_person.links.attributes[0].value == "true"
    assert any(item.code == "invalid_metadata_value" for item in model.diagnostics)

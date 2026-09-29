from gramps_fancy_book.domain import (
    EditorialBook,
    EditorialCitationCall,
    EditorialCitationEntry,
    EditorialFamilyNotice,
    EditorialProfile,
)
from gramps_fancy_book.renderers.citation_numbers import citation_number_map


def test_citation_number_map_uses_the_requested_context_order():
    family_notice = EditorialFamilyNotice(
        notice_id="family-notice:f1",
        family_handle="f1",
        primary_section_id="family-section:f1",
        citation_call_ids=("family-call",),
    )
    profile = EditorialProfile(
        profile_id="profile:p1",
        person_handle="p1",
        citation_call_ids=("profile-call",),
    )
    family_call = EditorialCitationCall(
        call_id="family-call",
        citation_handle="family-citation",
        context_id=family_notice.notice_id,
        owner_type="family",
        owner_handle="f1",
        field_path="family",
    )
    profile_call = EditorialCitationCall(
        call_id="profile-call",
        citation_handle="profile-citation",
        context_id=profile.profile_id,
        owner_type="person",
        owner_handle="p1",
        field_path="person",
    )
    family_entry = EditorialCitationEntry(
        entry_id="citation:family-citation",
        citation_handle="family-citation",
        calls=(family_call,),
    )
    profile_entry = EditorialCitationEntry(
        entry_id="citation:profile-citation",
        citation_handle="profile-citation",
        calls=(profile_call,),
    )
    book = EditorialBook(
        profiles=(profile,),
        family_notices=(family_notice,),
        citation_entries=(profile_entry, family_entry),
    )

    assert citation_number_map(book) == {
        "citation:family-citation": 1,
        "citation:profile-citation": 2,
    }
    assert citation_number_map(
        book,
        context_order=(profile.profile_id, family_notice.notice_id),
    ) == {
        "citation:profile-citation": 1,
        "citation:family-citation": 2,
    }

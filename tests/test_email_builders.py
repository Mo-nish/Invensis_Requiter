from email_service import build_role_assignment_body, build_candidate_assignment_body


class CandidateStub:
    def __init__(self):
        self.first_name = "Jane"
        self.last_name = "Doe"
        self.experience = 5
        self.email = "jane@example.com"
        self.phone = "123"
        self.reference_id = "REF-1"


def test_build_role_assignment_body_contains_role_and_link():
    body = build_role_assignment_body("manager")
    assert "Manager" in body
    assert "/register" in body


def test_build_candidate_assignment_body_contains_fields():
    c = CandidateStub()
    body = build_candidate_assignment_body(c, None)
    for s in [c.first_name, c.last_name, c.email, c.reference_id]:
        assert s in body



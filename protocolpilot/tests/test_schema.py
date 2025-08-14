from protocol_pilot.schema import Protocol, Step, Reagent, validate_protocol

def test_minimal_protocol_valid():
    p = Protocol(
        title="Example",
        sources=["DOI:10.0000/example"],
        equipment=["pipette"],
        reagents=[Reagent(name="water")],
        steps=[Step(number=1, description="Do a thing.")],
        safety_notes=["Wear PPE"],
        ruo_disclaimer="Research Use Only (RUO). Not for use in diagnostic procedures or patient care.",
    )
    validate_protocol(p)  # should not raise

def test_steps_must_be_sequential():
    try:
        Protocol(
            title="Bad",
            sources=["x"],
            steps=[Step(number=2, description="oops")],
            ruo_disclaimer="Research Use Only (RUO).",
        )
    except Exception:
        assert True
    else:
        assert False, "Expected an error for non-sequential steps"

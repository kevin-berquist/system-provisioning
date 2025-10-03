from app.services import make_filename

def test_make_filename_pattern():
    fn = make_filename('dev')
    assert fn.startswith('dev-')
    assert fn.endswith('.json')

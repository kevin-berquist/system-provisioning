from app.services import make_filename

def test_make_filename_pattern_default():
    fn = make_filename('dev')
    assert fn.startswith('dev-')
    assert fn.endswith('.json')

def test_make_filename_with_extension():
    fn = make_filename('prod', extension='.jsontest')
    assert fn.startswith('prod-')
    assert fn.endswith('.jsontest')

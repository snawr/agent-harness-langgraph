def test_main_module_is_importable_without_starting_a_run():
    import main

    assert callable(main.main)

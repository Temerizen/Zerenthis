def run_tests():
    try:
        import backend.app.main
        return True
    except:
        return False

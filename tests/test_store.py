import threading

from recon.store import ResultStore


def test_store_write_query(tmp_path):
    with ResultStore(tmp_path / "x.db") as store:
        result_id = store.save({"left": "a.csv"}, {"differences": [{"status": "left_only", "left_table": "a.csv"}]}, {"a.csv": "abc"})
        rows = store.query(table_name="a.csv", severity="fatal")
    assert rows[0]["id"] == result_id and rows[0]["difference_count"] == 1


def test_store_concurrent_writes(tmp_path):
    path = tmp_path / "x.db"
    def write(index):
        with ResultStore(path) as store:
            store.save({"run": index}, {"differences": []})
    threads = [threading.Thread(target=write, args=(index,)) for index in range(8)]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    with ResultStore(path) as store: assert len(store.query(limit=20)) == 8

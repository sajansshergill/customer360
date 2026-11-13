import duckdb

from consumer360.ingestion.loader import load_all_bronze


def test_load_samples_into_temp_duckdb(tmp_settings):
    counts = load_all_bronze(tmp_settings)
    assert counts["sap_cdc"] >= 1
    con = duckdb.connect(str(tmp_settings.warehouse_path), read_only=True)
    try:
        n = con.execute("SELECT count(*) FROM bronze_sap_cdc_profiles").fetchone()[0]
        assert n >= 1
        cols = {r[0] for r in con.execute("DESCRIBE bronze_sap_cdc_profiles").fetchall()}
        assert "_loaded_at" in cols
    finally:
        con.close()

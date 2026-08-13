import unittest
from src.parser.metadata_extractor import MetadataExtractor

class TestMetadataExtractor(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = MetadataExtractor()

    def test_extract_standard_filename(self) -> None:
        filename = "AAA_financial_statements_2023_consolidated.txt"
        metadata = self.extractor.extract(filename)
        
        self.assertEqual(metadata.source, filename)
        self.assertEqual(metadata.additional_info.get("ticker"), "AAA")
        self.assertEqual(metadata.additional_info.get("year"), "2023")
        self.assertEqual(metadata.additional_info.get("report_type"), "consolidated")
        self.assertEqual(metadata.additional_info.get("filename"), filename)

    def test_extract_short_filename(self) -> None:
        filename = "VNM_2022_audited.pdf"
        metadata = self.extractor.extract(filename)
        
        self.assertEqual(metadata.additional_info.get("ticker"), "VNM")
        self.assertEqual(metadata.additional_info.get("year"), "2022")
        self.assertEqual(metadata.additional_info.get("report_type"), "audited")

    def test_extract_complex_report_type(self) -> None:
        filename = "FPT_BCTC_2021_Q2_review.csv"
        metadata = self.extractor.extract(filename)
        
        self.assertEqual(metadata.additional_info.get("ticker"), "FPT")
        self.assertEqual(metadata.additional_info.get("year"), "2021")
        self.assertEqual(metadata.additional_info.get("report_type"), "q2_review")

    def test_extract_invalid_filename(self) -> None:
        filename = "random_document_no_year.txt"
        metadata = self.extractor.extract(filename)
        
        self.assertEqual(metadata.source, filename)
        self.assertNotIn("ticker", metadata.additional_info)
        self.assertNotIn("year", metadata.additional_info)
        self.assertNotIn("report_type", metadata.additional_info)
        self.assertEqual(metadata.additional_info.get("filename"), filename)

    def test_extract_full_filepath(self) -> None:
        filepath = "/var/data/reports/MBB_report_2024_unaudited.txt"
        metadata = self.extractor.extract(filepath)
        
        # The extractor should only parse the filename part
        expected_name = "MBB_report_2024_unaudited.txt"
        self.assertEqual(metadata.source, expected_name)
        self.assertEqual(metadata.additional_info.get("ticker"), "MBB")
        self.assertEqual(metadata.additional_info.get("year"), "2024")
        self.assertEqual(metadata.additional_info.get("report_type"), "unaudited")

if __name__ == '__main__':
    unittest.main()

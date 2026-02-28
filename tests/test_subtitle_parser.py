import os
import tempfile
import unittest
from core.subtitle_parser import SubtitleParser

class TestSubtitleParser(unittest.TestCase):
    def setUp(self):
        # Create a temporary SRT file
        self.fd, self.srt_path = tempfile.mkstemp(suffix=".srt")
        with os.fdopen(self.fd, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:01,000 --> 00:00:02,500\n这是第一句话\n测试换行合并\n\n")
            f.write("2\n00:00:03,000 --> 00:00:05,000\n这是第二句话\n")
            
    def tearDown(self):
        os.remove(self.srt_path)
        
    def test_parse_valid_srt(self):
        parser = SubtitleParser(self.srt_path)
        items = parser.parse()
        
        self.assertEqual(len(items), 2)
        
        # Check first item calculations
        self.assertEqual(items[0].index, 1)
        self.assertEqual(items[0].start_time_ms, 1000)
        self.assertEqual(items[0].end_time_ms, 2500)
        self.assertEqual(items[0].duration_ms, 1500)
        self.assertEqual(items[0].text, "这是第一句话 测试换行合并") # Verify newline replacement
        
        # Check second item calculations
        self.assertEqual(items[1].index, 2)
        self.assertEqual(items[1].start_time_ms, 3000)
        self.assertEqual(items[1].end_time_ms, 5000)
        self.assertEqual(items[1].duration_ms, 2000)
        self.assertEqual(items[1].text, "这是第二句话")

    def test_parse_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            SubtitleParser("non_existent_file.srt")

if __name__ == '__main__':
    unittest.main()

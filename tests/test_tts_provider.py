import unittest
from unittest.mock import patch
from core.tts_provider import Pyttsx3TTS, HttpTTS

class TestTTSProvider(unittest.TestCase):
    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    @patch('os.remove')
    def test_mac_fallback(self, mock_remove, mock_exists, mock_run):
        tts = Pyttsx3TTS()
        self.assertTrue(tts.is_mac)
        
        # Simulate successful audio generation
        result = tts.generate_audio("Hello", "output.wav")
        self.assertTrue(result)
        
        # Check if native 'say' and 'ffmpeg' processes were called
        self.assertEqual(mock_run.call_count, 2)
        
        # Validate 'say' invocation
        args_say = mock_run.call_args_list[0][0][0]
        self.assertIn('say', args_say)
        
        # Validate 'ffmpeg' format conversion invocation
        args_ffmpeg = mock_run.call_args_list[1][0][0]
        self.assertIn('ffmpeg', args_ffmpeg)

    @patch('urllib.request.urlopen')
    def test_http_tts_success(self, mock_urlopen):
        # Mocking http response
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.status = 200
        mock_response.read.return_value = b'fake_audio_data'
        
        tts = HttpTTS()
        with patch('builtins.open', unittest.mock.mock_open()) as mocked_file:
            result = tts.generate_audio("Test", "mock.wav")
            self.assertTrue(result)
            mocked_file.assert_called_with("mock.wav", 'wb')
            mocked_file().write.assert_called_with(b'fake_audio_data')

if __name__ == '__main__':
    unittest.main()

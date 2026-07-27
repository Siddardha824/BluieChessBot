import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QProcess
from gui.app.engine.services.engine_connector import EngineConnector


class TestEngineConnector:
    """Test suite for the EngineConnector service wrapper."""

    @pytest.fixture
    def mock_qprocess(self):
        """Fixture to patch and mock the QProcess inside the EngineConnector.

        Preserves real enum constants on the QProcess mock class to ensure
        comparisons and parameter assertions match perfectly.
        """
        with patch("gui.app.engine.services.engine_connector.QProcess") as mock_class:
            mock_proc = MagicMock()
            mock_class.return_value = mock_proc

            # Preserve real enums on the mock class to avoid mock equality mismatches
            mock_class.ProcessChannelMode = QProcess.ProcessChannelMode
            mock_class.ProcessState = QProcess.ProcessState
            mock_class.ProcessError = QProcess.ProcessError
            mock_class.ExitStatus = QProcess.ExitStatus

            yield mock_proc

    @pytest.fixture
    def connector(self, mock_qprocess):
        """Fixture to provide a fresh EngineConnector instance with a mocked QProcess."""
        return EngineConnector(parent=None)

    # --- Initialization Tests ---

    def test_initialization(self, mock_qprocess, connector):
        """Verify that the engine connector configures standard I/O channels and connects internal slots."""
        mock_qprocess.setProcessChannelMode.assert_called_once_with(QProcess.ProcessChannelMode.SeparateChannels)
        mock_qprocess.readyReadStandardOutput.connect.assert_called_once_with(connector._handle_ready_read_stdout)
        mock_qprocess.readyReadStandardError.connect.assert_called_once_with(connector._handle_ready_read_stderr)
        mock_qprocess.errorOccurred.connect.assert_called_once_with(connector._handle_process_error)
        mock_qprocess.finished.connect.assert_called_once_with(connector._handle_process_finished)

    # --- Start Subprocess Tests ---

    @patch("gui.app.engine.services.engine_connector.os.path.exists")
    def test_start_already_running(self, mock_exists, mock_qprocess, connector):
        """Verify start returns True immediately if the engine subprocess is already active."""
        mock_qprocess.state.return_value = QProcess.ProcessState.Running
        mock_qprocess.waitForStarted.return_value = True

        assert connector.start("dummy_path") is True
        mock_qprocess.start.assert_not_called()
        mock_exists.assert_not_called()

    @patch("gui.app.engine.services.engine_connector.os.path.exists")
    def test_start_executable_not_found(self, mock_exists, mock_qprocess, connector):
        """Verify start returns False if the executable file does not exist on disk."""
        mock_qprocess.state.return_value = QProcess.ProcessState.NotRunning
        mock_exists.return_value = False

        assert connector.start("invalid_path") is False
        mock_qprocess.start.assert_not_called()

    @patch("gui.app.engine.services.engine_connector.os.path.exists")
    def test_start_successful(self, mock_exists, mock_qprocess, connector):
        """Verify start calls start on QProcess and returns True if wait for started succeeds."""
        mock_qprocess.state.return_value = QProcess.ProcessState.NotRunning
        mock_exists.return_value = True
        mock_qprocess.waitForStarted.return_value = True

        assert connector.start("valid_path") is True
        mock_qprocess.start.assert_called_once_with("valid_path")
        mock_qprocess.waitForStarted.assert_called_once_with(250)

    @patch("gui.app.engine.services.engine_connector.os.path.exists")
    def test_start_failed_timeout(self, mock_exists, mock_qprocess, connector):
        """Verify start returns False if the process fails to start within the 250ms threshold."""
        mock_qprocess.state.return_value = QProcess.ProcessState.NotRunning
        mock_exists.return_value = True
        mock_qprocess.waitForStarted.return_value = False

        assert connector.start("valid_path") is False
        mock_qprocess.start.assert_called_once_with("valid_path")

    # --- Stop Subprocess Tests ---

    def test_stop_when_idle(self, mock_qprocess, connector):
        """Verify stop does nothing if the process is not currently running."""
        mock_qprocess.state.return_value = QProcess.ProcessState.NotRunning

        connector.stop()

        mock_qprocess.write.assert_not_called()
        mock_qprocess.terminate.assert_not_called()

    def test_stop_graceful_exit(self, mock_qprocess, connector):
        """Verify stop writes the quit command and waits for standard graceful termination."""
        mock_qprocess.state.return_value = QProcess.ProcessState.Running
        mock_qprocess.waitForFinished.return_value = True

        connector.stop()

        mock_qprocess.write.assert_called_once_with(b"quit\n")
        mock_qprocess.waitForFinished.assert_called_once_with(300)
        mock_qprocess.terminate.assert_not_called()

    def test_stop_force_terminate_fallback(self, mock_qprocess, connector):
        """Verify stop forcefully terminates the process if the engine fails to exit gracefully within 300ms."""
        mock_qprocess.state.return_value = QProcess.ProcessState.Running
        mock_qprocess.waitForFinished.return_value = False

        connector.stop()

        mock_qprocess.write.assert_called_once_with(b"quit\n")
        mock_qprocess.waitForFinished.assert_called_once_with(300)
        mock_qprocess.terminate.assert_called_once()

    # --- Send Commands Tests ---

    def test_send_command_success(self, mock_qprocess, connector):
        """Verify send encodes and writes the command string to process stdin when active."""
        mock_qprocess.state.return_value = QProcess.ProcessState.Running

        connector.send("go infinite")

        mock_qprocess.write.assert_called_once_with(b"go infinite\n")

    def test_send_command_ignored_when_offline(self, mock_qprocess, connector):
        """Verify send is ignored if the process is not in the Running state."""
        mock_qprocess.state.return_value = QProcess.ProcessState.NotRunning

        connector.send("go infinite")

        mock_qprocess.write.assert_not_called()

    # --- Telemetry & State Slot Tests ---

    def test_handle_ready_read_stdout(self, mock_qprocess, connector):
        """Verify stdout reading drains all available lines and emits stdout_received signals."""
        mock_qprocess.canReadLine.side_effect = [True, True, False]

        mock_line1 = MagicMock()
        mock_line1.data.return_value = b"info depth 5\n"
        mock_line2 = MagicMock()
        mock_line2.data.return_value = b"bestmove d2d4\n"
        mock_qprocess.readLine.side_effect = [mock_line1, mock_line2]

        received_lines = []
        connector.stdout_received.connect(received_lines.append)

        connector._handle_ready_read_stdout()

        assert received_lines == ["info depth 5", "bestmove d2d4"]

    def test_handle_ready_read_stderr(self, mock_qprocess, connector):
        """Verify stderr reading parses diagnostic logs and emits stderr_received signals."""
        mock_stderr = MagicMock()
        mock_stderr.data.return_value = b"Critical engine warning\n"
        mock_qprocess.readAllStandardError.return_value = mock_stderr

        received_stderr = []
        connector.stderr_received.connect(received_stderr.append)

        connector._handle_ready_read_stderr()

        assert received_stderr == ["Critical engine warning"]

    @pytest.mark.parametrize(
        "error_enum, expected_message",
        [
            (QProcess.ProcessError.FailedToStart, "Failed to start process"),
            (QProcess.ProcessError.Crashed, "Process crashed"),
            (QProcess.ProcessError.Timedout, "Process timed out"),
            (QProcess.ProcessError.WriteError, "Write error"),
            (QProcess.ProcessError.ReadError, "Read error"),
            (QProcess.ProcessError.UnknownError, "Unknown process error"),
        ]
    )
    def test_handle_process_error(self, error_enum, expected_message, mock_qprocess, connector):
        """Verify process error callback maps error codes to standard text and signals the GUI."""
        received_errors = []
        connector.process_error.connect(received_errors.append)

        connector._handle_process_error(error_enum)

        assert received_errors == [expected_message]

    def test_handle_process_finished(self, mock_qprocess, connector):
        """Verify process termination emits the exit status and code parameters."""
        received_finished = []
        connector.process_finished.connect(lambda code, status: received_finished.append((code, status)))

        connector._handle_process_finished(0, QProcess.ExitStatus.NormalExit)

        assert received_finished == [(0, QProcess.ExitStatus.NormalExit)]

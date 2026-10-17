def write_all(self, data: bytes) -> None:
        assert self.fd is not None
        total = 0
        while total < len(data):
            _, ready, _ = select.select([], [self.fd], [], self.timeout_sec)
            if not ready:
                raise ToolError("timed out waiting for serial port write availability")
            written = os.write(self.fd, data[total:])
            if written <= 0:
                raise ToolError("serial write returned no progress")
            total += written

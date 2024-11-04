class RDB:
    def __init__(self, dir_path, db_filename):
        self.db = None
        self.dir_path = dir_path
        self.db_filename = db_filename


    async def handle_client(self, reader, writer):
        while True:
            data = await reader.read(100)
            if not data:
                break
            message = data.decode().strip()
            command_parts = message.split()

            if len(command_parts) != 3 or command_parts[0].upper() != "CONFIG" or command_parts[1].upper() != "GET":
                writer.write(b"-ERR unknown command\r\n")
                await writer.drain()
                continue

            param = command_parts[2]

            if param == "dir":
                response = f"$3\r\n{self.dir_path}\r\n"
            elif param == "dbfilename":
                response = f"${len(self.db_filename)}\r\n{self.db_filename}\r\n"
            else:
                response = "$-1\r\n"

            writer.write(response.encode('utf-8'))
            await writer.drain()

        writer.close()
        await writer.wait_closed()
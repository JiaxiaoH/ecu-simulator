from tkinter import filedialog    
def export_treeview_to_blf(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".blf",
            filetypes=[("BLF Files", "*.blf"), ("All Files", "*.*")],
            title="Save as BLF"
        )
        if not file_path:
            return
        writer = can.BLFWriter(file_path)
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if len(values) < 3:
                continue
            time_str, direction, data_str, session, security, *_ = values
            try:
                timestamp = datetime.datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S.%f").timestamp()
            except ValueError:
                timestamp = datetime.datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S").timestamp()
            try:
                data_list = bytes(int(x, 16) for x in data_str.split())
            except ValueError:
                continue
            if len(data_list)>64:
                data_list=data_list[:64]
            data=bytes(data_list)

            is_rx = True if direction.upper() == "RX" else False
            #is_extended_id = True if len(data)>8 else False
            msg = can.Message(
                timestamp=timestamp,
                arbitration_id=0x7E0 if not is_rx else 0x7E8,
                data=data,
                is_extended_id=False,
                is_fd=True,
                is_rx=is_rx,
                channel=0,
            )
            writer.on_message_received(msg)
        writer.stop()
        print(f"Exported Treeview data to BLF file: {file_path}")
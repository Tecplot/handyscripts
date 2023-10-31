import tecplot as tp
tp.session.connect()

def copy_all_frames_to_new_page(src_page, new_page_name):
	new_page = tp.add_page()
	new_page.name = new_page_name	
	new_page_default_frame = new_page.active_frame()
	for frame in src_page.frames():
		frame.activate()
		position = frame.position
		print(frame, frame.position)
		tp.macro.execute_command(f"""$!Pick AddAtPosition
X = {position[0]}
Y = {position[1]}""")
		tp.macro.execute_command("$!Pick Copy")
		new_page.activate()
		tp.macro.execute_command("$!Pick Paste")
	new_page.delete_frame(new_page_default_frame)


new_page_name = input("Enter the new page name: ")
copy_all_frames_to_new_page(tp.active_page(), new_page_name)



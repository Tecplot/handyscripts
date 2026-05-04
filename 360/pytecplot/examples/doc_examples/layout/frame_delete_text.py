import tecplot as tp

text = tp.active_frame().add_text("abc")
tp.active_frame().delete_text(text)

# The text object is no longer valid.
# Any property access will throw TecplotLogicError
try:
    print(text.text_string)
except tp.exception.TecplotLogicError as e:
    print(e)

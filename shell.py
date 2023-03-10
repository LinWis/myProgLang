import montel

while True:
    text = input("montel> ")
    if text.strip() == "": continue
    result, error = montel.run('<stdin>', text)

    if error:
        print(error.as_string())
    elif result:
        if len(result.elements) == 1:
            if result.elements[0].value != 0:
                print(repr(result.elements[0]))
        else:
            print(repr(result))

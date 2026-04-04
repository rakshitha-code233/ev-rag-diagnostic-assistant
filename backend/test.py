from query import get_answer

while True:
    q = input("Ask: ")
    if q.lower() == "exit":
        break

    answer = get_answer(q)
    print("Answer:", answer)
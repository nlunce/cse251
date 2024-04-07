import threading
import time

done = False


def worker():
    counter = 0
    while not done:
        time.sleep(1)
        counter += 1
        print(counter)


t1 = threading.Thread(target=worker)
t2 = threading.Thread(target=worker)

t1.join()


input("Press enter to quit")
done = True

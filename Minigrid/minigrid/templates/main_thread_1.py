"""

import threading


def add_numbers_to_dict(start, end, shared_dict, count):
    local_count = 0  # Local count variable for this thread
    for i in range(start, end + 1):
        shared_dict[i] = True
        local_count += 1  # Increment local count for each addition
    print(
        f"Thread added {local_count} numbers from {start} to {end} to the dictionary."
    )
    count += local_count  # Increment the main count by local count
    print(count)
    return count


def main():
    shared_dict = {}
    count = 0  # Initialize count in main

    thread1 = threading.Thread(
        target=add_numbers_to_dict, args=(1, 5, shared_dict, count)
    )
    thread2 = threading.Thread(
        target=add_numbers_to_dict, args=(6, 10, shared_dict, count)
    )

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print("Keys in the dictionary:", list(shared_dict.keys()))
    print("Total count:", count)  # Print the total count at the end


if __name__ == "__main__":
    main()
"""

"""
import threading


# Function to increment count
def increment_count(lock, count):
    for _ in range(1000000):  # Increment count 1 million times
        with lock:
            count += 1


# Main function
def main():
    count = 0  # Shared count variable
    lock = threading.Lock()  # Lock to synchronize access to count

    # Create two threads
    thread1 = threading.Thread(target=increment_count, args=(lock, count))
    thread2 = threading.Thread(target=increment_count, args=(lock, count))

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for the threads to finish
    thread1.join()
    thread2.join()

    # Print the final value of count
    print("Final count value:", count)


if __name__ == "__main__":
    main()
"""


import threading


# Function to increment count
def increment_count(lock, count):
    for _ in range(1000000):  # Increment count 1 million times
        with lock:
            count[0] += 1


# Main function
def main():
    count = [0]  # Shared count variable wrapped in a list
    lock = threading.Lock()  # Lock to synchronize access to count

    # Create two threads
    thread1 = threading.Thread(target=increment_count, args=(lock, count))
    thread2 = threading.Thread(target=increment_count, args=(lock, count))

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for the threads to finish
    thread1.join()
    thread2.join()

    # Print the final value of count
    print(count)
    print("Final count value:", count[0])


if __name__ == "__main__":
    main()

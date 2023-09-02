import json
from multiprocessing import Process
import multiprocessing
from swedish_sortition import Sortition
import pandas as pd

if __name__ == "__main__":  # confirms that the code is under main function
    df = pd.read_csv('fake_people.csv')

    with open('criteria.json.example') as f:
        criteria = json.load(f)

    sortition = Sortition(criteria, 70)

    if __name__ == "__main__":
        procs = []

        for i in range(multiprocessing.cpu_count() - 1):
            # print(name)
            proc = Process(
                    target=sortition.generate_samples,
                    args=(1000000, 'lottning', df))
            procs.append(proc)
            proc.start()

        # complete the processes
        for proc in procs:
            proc.join()

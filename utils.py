import random
from deap import base
from deap import creator
from deap import tools
import array
import random
import json
import numpy as np
from math import sqrt
from deap import algorithms
from deap import base
from deap import benchmarks
from deap.benchmarks.tools import diversity, convergence, hypervolume
from deap import creator
from deap import tools
from random import shuffle
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from  selenium.webdriver.common.action_chains import ActionChains
import argparse
from read_gremlins_logs import parse_line, Ind
from datetime import datetime
from selenium.webdriver.common.touch_actions import TouchActions
from time import sleep, time
from peewee import *
import os
from selenium.webdriver.chrome.options import Options
db = SqliteDatabase('errors.db')
class ErrorModel(Model):
    timestamp = IntegerField()
    sequence_length = IntegerField()
    number_errors = IntegerField()
    sequence = TextField()
    errors = TextField()
    class Meta:
        database = db # This model uses the "people.db" database.
db.create_tables([ErrorModel])
parser = argparse.ArgumentParser()
parser.add_argument(
    "--url",
    help="echo the url you use here")
parser.add_argument(
    "--ngen",
    default=10,
    help="echo the number of generations you use here")
parser.add_argument(
    "--npop",
    default=2,
    help="echo the number of populations you use here")
parser.add_argument(
    "--nchromo",
    default=2,
    help="echo the number of chromosomes you use here")
parser.add_argument(
    "--headless",
    default=1,
    help="headless evaluation; 0 for no, 1 for yes")
args = parser.parse_args()
num_chromosomes = int(args.nchromo)
creator.create("FitnessMulti", base.Fitness, weights=(-1.0, 1.0))
creator.create("TestCase", list, fitness=creator.FitnessMulti, testcase=None, best=None)
to_cur = 0
def read_large_file(file_object):
    global to_cur
    """
    Uses a generator to read a large file lazily
    """
    while True:
        skip = 0
        while skip <= to_cur:
            data = file_object.readline()
            skip += 1
        to_cur = skip
        if not data:
            break
        yield data
def initTestCase(size):
    ret = []
    path = "genes.csv"
    try:
        with open(path) as file_handler:
            i = 0
            for line in read_large_file(file_handler):
                # process line
                ret.append(line)
                i += 1
                if i >= size:
                    break
    except (IOError, OSError):
        print("Error opening / processing file")
    return ret
toolbox = base.Toolbox()
toolbox.register("testcase", initTestCase, creator.TestCase, size=num_chromosomes)
def uniform(low, up, size=None):
    try:
        return [random.uniform(a, b) for a, b in zip(low, up)]
    except TypeError:
        return [random.uniform(a, b) for a, b in zip([low] * size, [up] * size)]
toolbox.register("attr_generator", initTestCase, num_chromosomes)
toolbox.register("individual", tools.initIterate, creator.TestCase, toolbox.attr_generator)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
def evaluate(individual, report=False, driver=None):
    errors = []
    # close_after_eval = False
    if not driver:
        # close_after_eval = True
        chrome_options = Options()
        if bool(int(args.headless)):
            chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=chrome_options)
    driver.get(args.url)
    """coverageJSON = driver.execute_script("return jscoverage_serializeCoverageToJSON();")
    file = open("jscoverage.json","w")
    file.write(coverageJSON)
    file.close()"""
    dict_dims = driver.get_window_size()
    max_width = dict_dims['width']
    max_height = dict_dims['height']
    for tc in individual:
        if type(tc) is str:
            o = parse_line(tc)
        else:
            o = tc
        if o is None:
            continue
        o.normalize_dimensions(max_width, max_height)
        if o.event == "type" or o.event == "input":
            elems = driver.find_elements_by_tag_name(o.dom)
            for elem in elems:
                try:
                    if elem and elem.is_displayed():
                        elem.send_keys(o.input)
                        elem.send_keys(Keys.RETURN)
                except:
                    actions = ActionChains(driver)
                    actions.send_keys(Keys.RETURN)
                    actions.perform()
                    # sleep(25)
        elif o.event == "scroll":
            actions = TouchActions(driver)
            actions.scroll(o.locx, o.locy)
            try:
                actions.perform()
            except:
                pass
        elif o.event == "tap" or o.event == "doubletap" or o.event == "multitouch":
            actions = TouchActions(driver)
            actions.tap_and_hold(o.locx, o.locy)
            try:
                actions.perform()
            except:
                pass
        else:
            actions = ActionChains(driver)
            actions.move_by_offset(o.locx, o.locy)
            actions.click()
            try:
                actions.perform()
            except:
                pass
    for entry in driver.get_log('browser'):
        errors.append(entry)
    # if close_after_eval:
    #     driver.close()
    obj1 = len(individual)
    obj2 = len(errors)
    if report is not False:
        report.write("Number of Errors: {} \n".format(len(errors)))
        report.write("Test Cases Length: {} \n".format(len(individual)))
        report.write("Errors Found:\n")
        report.write(str(errors))
        report.write("\n")
        report.write("Test Cases:\n")
        report.write(str(list(individual)))
        row = ErrorModel(timestamp=int(time()), sequence_length=len(individual), number_errors=len(errors),
                   sequence=str(list(individual)), errors=str(errors))
        row.save()
    return obj1, obj2
def mate(a, b):
    shuffle(a)
    new_genes = random.choice([8, 16, 32, 64, 128])
    for i in range(new_genes):
        a.insert(np.random.randint(0, len(a)), synthesize())
    choice = np.random.randint(0, 2)
    if choice == 0:
        ret = a.extend(b)
    elif choice == 1:
        ret = b.extend(a)
    return ret
def synthesize():
    if np.random.randint(0, 1e3) % 2 == 0:
        tc = Ind(_e="click")
    elif np.random.randint(0, 1e3) % 3 == 0:
        tc = Ind(_e="scroll")
    else:
        tc = Ind(_e="type")
    tc.fuzzy()
    return tc
MUTPB = 0.3
def mutate(individual, indpb):
    # shuffle seq
    individual, = tools.mutShuffleIndexes(individual, indpb)
    # crossover inside the suite
    for i in range(1, len(list(individual)), 2):
        if random.random() < MUTPB:
            if len(list(individual)) <= 2:
                continue  # sys.exit(1)
            if len(list(individual)) <= 2:
                continue  # sys.exit(1)
            individual[i - 1], individual[i] = tools.cxBlend(individual[i - 1], individual[i], 0.7)
    # shuffle events
    for i in range(len(list(individual))):
        if random.random() < MUTPB:
            if len(list(individual)) <= 2:
                continue  # sys.exit(1)
            list(individual)[i], = tools.mutShuffleIndexes(list(individual)[i], indpb)
    return individual
toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.5)
toolbox.register("select", tools.selNSGA2)
def main(seed=None):
    random.seed(seed)
    NGEN = int(args.ngen)
    MU = int(args.npop)
    CXPB = 0.9
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    # stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)
    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "min", "avg", "max"
    pop = toolbox.population(n=MU)
    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select(pop, len(pop))
    record = stats.compile(pop)
    logbook.record(gen=0, evals=len(invalid_ind), **record)
    print(logbook.stream)
    # Begin the generational process
    for gen in range(1, NGEN):
        # Vary the population
        offspring = tools.selTournamentDCD(pop, len(pop))
        offspring = [toolbox.clone(ind) for ind in offspring]
        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= CXPB:
                toolbox.mate(ind1, ind2)
            toolbox.mutate(ind1)
            toolbox.mutate(ind2)
            del ind1.fitness.values, ind2.fitness.values
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        # Select the next generation population
        pop = toolbox.select(pop + offspring, MU)
        record = stats.compile(pop)
        logbook.record(gen=gen, evals=len(invalid_ind), **record)
        print(logbook.stream)
    print("Final population hypervolume is %f" % hypervolume(pop, [11.0, 11.0]))
    return pop, logbook
if __name__ == "__main__":
    pop, stats = main()
    chrome_options = Options()
    if bool(int(args.headless)):
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=chrome_options)
    driver.get(args.url)
    with open("report_{:%B_%d_%Y}.txt".format(datetime.now()), "w") as f:
        for ind in pop:
            f.write(str(ind))
            f.write("\n")
            evaluate(ind, f, driver)
    driver.close()
    #os.rename("genes.csv", "genes-{}.csv".format(datetime.now()))
    import matplotlib.pyplot as plt
    gen, avg, min_, max_ = stats.select("gen", "avg", "min", "max")
    np_min = np.array(min_)
    np_avg = np.array(avg)
    np_max = np.array(max_)
    fig, axes = plt.subplots(2, 3)
    # first objective
    axes[0, 0].plot(gen, np_avg[:, 0], label="average length")
    axes[0, 0].set_title("Average Test Case Length")
    axes[0, 0].set_xlabel("Generation")
    axes[0, 0].set_ylabel("Objective #1: Test Case Length")
    axes[0, 1].plot(gen, np_min[:, 0], label="minimum length")
    axes[0, 1].set_title("Minimum Test Case Length")
    axes[0, 1].set_xlabel("Generation")
    axes[0, 1].set_ylabel("Objective #1: Test Case Length")
    axes[0, 2].plot(gen, np_max[:, 0], label="maximum length")
    axes[0, 2].set_title("Maximum Test Case Length")
    axes[0, 2].set_xlabel("Generation")
    axes[0, 2].set_ylabel("Objective #1: Test Case Length")
    # second objective
    axes[1, 0].plot(gen, np_avg[:, 1], label="average errors")
    axes[1, 0].set_title("Average Error Revelation")
    axes[1, 0].set_xlabel("Generation")
    axes[1, 0].set_ylabel("Objective #2: Number of Errors")
    axes[1, 1].plot(gen, np_min[:, 1], label="minimum errors")
    axes[1, 1].set_title("Minimum Error Revelation")
    axes[1, 1].set_xlabel("Generation")
    axes[1, 1].set_ylabel("Objective #2: Number of Errors")
    axes[1, 2].plot(gen, np_max[:, 1], label="maximum errors")
    axes[1, 2].set_title("Maximum Error Revelation")
    axes[1, 2].set_xlabel("Generation")
    axes[1, 2].set_ylabel("Objective #2: Number of Errors")
    plt.tight_layout()
    plt.show()

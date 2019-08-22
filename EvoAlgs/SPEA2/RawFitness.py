def dominates(src, target):
    src_is_worse = False
    equal = True
    for idx in range(len(src.objectives)):
        if src_is_worse:
            break
        src_is_worse = src.objectives[idx] > target.objectives[idx]
        equal = (src.objectives[idx] == target.objectives[idx]) and equal

    return (not equal) and (not src_is_worse)


def strength(pop):
    str_values = [0] * len(pop)
    for i in range(len(pop)):
        for j in range(len(pop)):
            if dominates(pop[i], pop[j]):
                str_values[i] += 1

    return str_values


def raw_fitness(pop):
    str_values = strength(pop)

    raw_values = [0] * len(pop)

    for i in range(len(pop)):
        raw_value = 0
        for j in range(len(pop)):
            if dominates(pop[j], pop[i]):
                raw_value += str_values[j]
        raw_values[i] = raw_value

    return raw_values
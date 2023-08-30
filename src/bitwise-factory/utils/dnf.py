import re

from implicant import Implicant, Bitwise, BitwiseType

usingGmpy = True
try: import gmpy2
except ModuleNotFoundError: usingGmpy = False

# Returns the number of ones in the given number's binary representation.
def popcount(x):
    if usingGmpy: return gmpy2.popcount(x)
    try: return x.bit_count()
    except AttributeError: return bin(x).count("1")


# A structure representing a disjunctive normal form, i.e., a disjunction of
# conjunctions of possibly negated variables.
class Dnf():
    # Initialize a disjunctive normal form with given number of variables and
    # the given truth value vector.
    def __init__(self, vnumber : int, vec : list[int]) -> None:
        self.__groups = []
        self.primes = []

        self.__init_groups(vnumber, vec)
        self.__merge()
        self.__drop_unrequired_implicants(vec)

    # Create a vector representation of conjunction for each 1 in the given
    # vector, equivalent to the corresponding evaluation of variables according
    # to its position, and classify the conjunctions according to their numbers
    # of ones.
    def __init_groups(self, vnumber : int, vec : list[int]) -> None:
        assert(len(vec) == 2**vnumber)

        self.__groups = [[] for i in range(vnumber + 1)]
        for i in range(len(vec)):
            bit = vec[i]

            if bit == 0: continue
            assert(bit == 1)

            onesCnt = popcount(i)
            self.__groups[onesCnt].append(Implicant(vnumber, i))

    # Try to merge implicants (i.e., vector representations of conjunctions)
    # whose vectors differ in just one position. Note that, e.g., the
    # disjunction of "x&y&z" and "x&y&~z" can be simplified to "x&y" since the
    # "z" has no influence on its values."
    def __merge_step(self) -> bool:
        changed = False
        newGroups = [[] for g in self.__groups]

        for onesCnt in range(len(self.__groups)):
            group = self.__groups[onesCnt]

            if onesCnt < len(self.__groups) - 1:
                nextGroup = self.__groups[onesCnt + 1]

                for impl1 in group:
                    for impl2 in nextGroup:
                        newImpl = impl1.try_merge(impl2)
                        # Could not merge the implicants.
                        if newImpl == None: continue

                        changed = True
                        impl1.obsolete = True
                        impl2.obsolete = True

                        newGroups[newImpl.count_ones()].append(newImpl)

            for impl in group:
                if not impl.obsolete:
                    self.primes.append(impl)

        self.__groups = newGroups
        return changed

    # Try to merge implicants iteratively until nothing can be merged any more.
    def __merge(self) -> None:
        while True:
            changed = self.__merge_step()

            if not changed:
                return

    # Remove impliciants which are already represented by others.
    def __drop_unrequired_implicants(self, vec : list[int]) -> None:
        requ = set([i for i in range(len(vec)) if vec[i] == 1])
        
        i = 0
        while i < len(self.primes):
            impl = self.primes[i]

            mtSet = set(impl.minterms)
            # The implicant has still required terms.
            if mtSet & requ:
                requ -= mtSet
                i += 1
                continue

            del self.primes[i]

    # Returns a string representation of this DNF.
    def __str__(self) -> str:
        s = "implicants:\n"

        for impl in self.primes:
            s += "    " + str(impl) + "\n"

        return s

    # Create an abstract syntax tree structure corresponding to this DNF.
    def to_bitwise(self) -> Bitwise:
        cnt = len(self.primes)
        if cnt == 0: return Bitwise(BitwiseType.TRUE, True)
        if cnt == 1: return self.primes[0].to_bitwise()

        root = Bitwise(BitwiseType.INCL_DISJUNCTION)
        for p in self.primes:
            root.add_child(p.to_bitwise())

        return root

    # Returns a more detailed string representation.
    def get(self, variables : list[str]) -> str:
        if len(self.primes) == 0: return "0"

        s = ""
        for p in self.primes:
            if len(s) > 0: s += "|"

            ps = p.get(variables)
            withPar = len(self.primes) > 1 and bool(re.search("([&])", ps))
            s += "(" + ps + ")" if withPar else ps

        return s

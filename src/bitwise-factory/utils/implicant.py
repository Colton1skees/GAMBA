from __future__ import annotations
from bitwise import Bitwise, BitwiseType

# A structure representing a conjunction of possibly negated variables. It is
# mainly represented as a vector whose entry with index 0 is 1 if the i-th
# variable occurs unnegatedly in the conjunction, 0 if it appears negatedly and
# None if it has no influence.
class Implicant():
    # Initialize an implicant for the given number of variables and the given
    # value whose binary representation constitutes the implicant's truth
    # values.
    def __init__(self, vnumber : int, value : int) -> None:
        self.vec = []
        self.minterms = [value] if value != -1 else []
        self.obsolete = False

        if value != -1:
            self.__init_vec(vnumber, value)

    # Initialize the implicant's vector with 1s for variables that appear
    # unnegatedly and 0s for those which appear negatedly.
    def __init_vec(self, vnumber : int, value : int) -> None:
        for i in range(vnumber):
            self.vec.append(value & 1)
            value >>= 1

        assert(len(self.vec) == vnumber)

    # Returns a string representation of this implicant.
    def __str__(self) -> str:
        return str(self.vec)

    # Returns a copy of this implicant.
    def __get_copy(self) -> Implicant:
        cpy = Implicant(len(self.vec), -1)
        cpy.vec = list(self.vec)
        cpy.minterms = list(self.minterms)
        return cpy

    # Returns the number of ones in the implicant's vector.
    def count_ones(self) -> int:
        return self.vec.count(1)

    # Try to merge this implicant with the given one. Returns a merged
    # implicant if this is possible and None otherwise.
    def try_merge(self, other : Implicant) -> Implicant:
        assert(len(self.vec) == len(other.vec))
        
        diffIdx = -1        
        for i in range(len(self.vec)):
            if self.vec[i] == other.vec[i]:
                continue

            # Already found a difference, no other difference allowed.
            if diffIdx != -1:
                return None
            
            diffIdx = i

        newImpl = self.__get_copy()
        newImpl.minterms += other.minterms
        if diffIdx != -1:
            newImpl.vec[diffIdx] = None

        return newImpl

    # Create an abstract syntax tree structure corresponding to this implicant.
    def to_bitwise(self) -> Bitwise:
        root = Bitwise(BitwiseType.CONJUNCTION)
        for i in range(len(self.vec)):
            # The variable has no influence.
            if self.vec[i] == None:
                continue

            root.add_variable(i, self.vec[i] == 0)

        cnt = root.child_count()
        if cnt == 0: return Bitwise(BitwiseType.TRUE)
        if cnt == 1: return root.first_child()
        return root

    # Returns a more detailed string representation.
    def get(self, variables : list[str]) -> str:
        assert(len(variables) == len(self.vec))
        
        s = ""
        for i in range(len(self.vec)):
            # The variable has no influence.
            if self.vec[i] == None:
                continue

            if len(s) > 0: s += "&"
            if self.vec[i] == 0: s += "~"
            s += variables[i]

        return s if len(s) > 0 else "-1"

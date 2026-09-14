import std.algorithm;
import std.array;
import std.conv;
import std.string;

string f(long[] nums) {
    nums.reverse();
    return nums.map!(n => n.to!string).join();
}

unittest
{
    alias candidate = f;

    assert(candidate([-1L, 9L, 3L, 1L, -2L]) == "-2139-1");
}
void main(){}

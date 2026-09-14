import std.math;
import std.typecons;
import std.array;
import std.algorithm;
import std.conv;
import std.string;

string f(string[] numbers, long num, long val) {
    if (num <= 1) {
        return numbers.join(" ");
    }

    while (numbers.length < num) {
        numbers.insertInPlace(numbers.length / 2, to!string(val));
    }

    long iterations = numbers.length / (num - 1) - 4;
    for (long i = 0; i < iterations; i++) {
        numbers.insertInPlace(numbers.length / 2, to!string(val));
    }

    return numbers.join(" ");
}

unittest
{
    alias candidate = f;

    assert(candidate([], 0L, 1L) == "");
}
void main(){}

import std.math;
import std.typecons;
import std.array;
import std.conv;
import std.string;

string[] f(long n) {
    auto b = to!string(n);
    string[] result = b.split("");
    foreach (i; 2 .. result.length) {
        result[i] ~= '+';
    }
    return result;
}

unittest
{
    alias candidate = f;

    assert(candidate(44L) == ["4", "4"]);
}
void main(){}

import std.math;
import std.typecons;
import std.uni;
import std.algorithm;

bool f(string text, string ch) {
    return ch.all!isLower && text.all!isLower;
}

unittest
{
    alias candidate = f;

    assert(candidate("abc", "e") == true);
}
void main(){}

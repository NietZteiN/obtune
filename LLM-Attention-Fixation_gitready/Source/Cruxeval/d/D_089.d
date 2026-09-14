import std.math;
import std.typecons;
import std.string;

string f(string ch) {
    if ("aeiouAEIOU".indexOf(ch) == -1) {
        return null;
    }
    if ("AEIOU".indexOf(ch) != -1) {
        return ch.toLower();
    }
    return ch.toUpper();
}

unittest
{
    alias candidate = f;

    assert(candidate("o") == "O");
}
void main(){}

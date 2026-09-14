import std.math;
import std.typecons;
import std.string;
import std.conv;

string f(string text) {
    foreach_reverse (i; 1 .. 11) {
        text = text.stripLeft(to!string(i));
    }
    return text;
}

unittest
{
    alias candidate = f;

    assert(candidate("25000   $") == "5000   $");
}
void main(){}

import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.ascii;
import std.conv;

string f(string doc) {
    foreach (x; doc) {
        if (x.isAlpha) {
            return std.ascii.toUpper(x).to!string;
        }
    }
    return "-";
}

unittest
{
    alias candidate = f;

    assert(candidate("raruwa") == "R");
}
void main(){}

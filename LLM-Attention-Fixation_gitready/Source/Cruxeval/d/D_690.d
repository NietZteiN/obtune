import std.math;
import std.typecons;
import std.string;
import std.conv;

string f(string n) {
    if (n.indexOf('.') != -1) {
        return to!string(to!int(n) + 2.5);
    }
    return n;
}

unittest
{
    alias candidate = f;

    assert(candidate("800") == "800");
}
void main(){}

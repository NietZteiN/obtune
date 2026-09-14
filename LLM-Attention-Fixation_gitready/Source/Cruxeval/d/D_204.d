import std.math;
import std.typecons;
import std.conv; // Import std.conv for the to function

string[] f(string name) {
    if (name.length < 2) {
        return [];
    }
    return [name[0].to!string, name[1].to!string];
}

unittest
{
    alias candidate = f;

    assert(candidate("master. ") == ["m", "a"]);
}
void main(){}

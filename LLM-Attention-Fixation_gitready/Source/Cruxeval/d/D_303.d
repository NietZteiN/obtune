import std.math;
import std.typecons;
import std.array;
import std.conv;
import std.string;

string f(string text) 
{
    size_t i = (text.length + 1) / 2;
    auto result = text.dup;
    while (i < text.length) {
        auto t = toLower(result[i].to!string)[0];
        if (t == result[i]) {
            i += 1;
        } else {
            result[i] = t;
        }
        i += 2;
    }
    return result.idup;
}
unittest
{
    alias candidate = f;

    assert(candidate("mJkLbn") == "mJklbn");
}
void main(){}

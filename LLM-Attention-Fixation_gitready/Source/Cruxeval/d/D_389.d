import std.math;
import std.typecons;
import std.array;
import std.string;

string[] f(string[] total, string arg) 
{
    if (arg.length > 1) {
        foreach (e; arg.split("")) {
            total ~= e;
        }
    } else {
        total ~= arg;
    }
    return total;
}
unittest
{
    alias candidate = f;

    assert(candidate(["1", "2", "3"], "nammo") == ["1", "2", "3", "n", "a", "m", "m", "o"]);
}
void main(){}

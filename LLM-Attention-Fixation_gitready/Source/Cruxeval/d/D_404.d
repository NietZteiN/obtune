import std.math;
import std.typecons;
import std.array;

long f(string[] no)
{
    bool[string] d;
    foreach (key; no)
        d[key] = false;
    return d.keys.length;
}
unittest
{
    alias candidate = f;

    assert(candidate(["l", "f", "h", "g", "s", "b"]) == 6L);
}
void main(){}

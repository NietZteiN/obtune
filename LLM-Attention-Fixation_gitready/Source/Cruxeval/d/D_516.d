import std.math;
import std.typecons;
import std.algorithm;
import std.array;

string[] f(string[] strings, string substr) 
{
    string[] list;
    foreach(s; strings) {
        if (s.startsWith(substr)) {
            list ~= s;
        }
    }
    list.sort!((a, b) => a.length < b.length);
    return list;
}
unittest
{
    alias candidate = f;

    assert(candidate(["condor", "eyes", "gay", "isa"], "d") == []);
}
void main(){}

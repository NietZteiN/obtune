import std.math;
import std.typecons;
import std.algorithm;
import std.array;

string[] f(string[] chemicals, long num) 
{
    string[] fish = chemicals[1 .. $];
    chemicals = chemicals.dup;
    chemicals.reverse();
    foreach (_; 0 .. num) {
        fish ~= chemicals[1];
        chemicals = chemicals[0 .. $ - 1];
    }
    chemicals.reverse();
    return chemicals;
}
unittest
{
    alias candidate = f;

    assert(candidate(["lsi", "s", "t", "t", "d"], 0L) == ["lsi", "s", "t", "t", "d"]);
}
void main(){}

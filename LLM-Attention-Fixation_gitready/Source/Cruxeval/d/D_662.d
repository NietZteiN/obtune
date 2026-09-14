import std.math;
import std.typecons;
import std.algorithm;

string[] f(string[] values) 
{
    string[] names = ["Pete", "Linda", "Angela"];
    names ~= values;
    names.sort();
    return names;
}
unittest
{
    alias candidate = f;

    assert(candidate(["Dan", "Joe", "Dusty"]) == ["Angela", "Dan", "Dusty", "Joe", "Linda", "Pete"]);
}
void main(){}

import std.math;
import std.typecons;
import std.array;
import std.string;

string[][] f(string[] text) 
{
    string[][] ls;
    foreach (x; text) {
        ls ~= x.splitLines();
    }
    return ls;
}
unittest
{
    alias candidate = f;

    assert(candidate(["Hello World
\"I am String\""]) == [["Hello World", "\"I am String\""]]);
}
void main(){}

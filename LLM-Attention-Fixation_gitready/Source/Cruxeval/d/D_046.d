import std.math;
import std.typecons;
import std.array;

string f(string[] l, string c) 
{
    return l.join(c);
}
unittest
{
    alias candidate = f;

    assert(candidate(["many", "letters", "asvsz", "hello", "man"], "") == "manylettersasvszhelloman");
}
void main(){}
